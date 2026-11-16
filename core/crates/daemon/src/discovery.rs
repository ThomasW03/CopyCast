//! Announces the daemon on the local network (mDNS / Zeroconf) so phones can find it.

use anyhow::{Context, Result};
use mdns_sd::{ServiceDaemon, ServiceInfo};

const SERVICE_TYPE: &str = "_copycast._tcp.local.";
const INSTANCE_NAME: &str = "CopyCast";
const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Starts advertising the control API. Stop it with [`ServiceDaemon::shutdown`].
pub fn advertise(port: u16) -> Result<ServiceDaemon> {
    let daemon = ServiceDaemon::new().context("cannot start the mDNS responder")?;
    let service = service_info(port)?;
    daemon
        .register(service)
        .context("cannot register the mDNS service")?;
    Ok(daemon)
}

fn service_info(port: u16) -> Result<ServiceInfo> {
    let properties = [("version", VERSION)];
    let service = ServiceInfo::new(
        SERVICE_TYPE,
        INSTANCE_NAME,
        &mdns_host_name()?,
        "",
        port,
        &properties[..],
    )
    .context("invalid mDNS service description")?;
    Ok(service.enable_addr_auto())
}

fn mdns_host_name() -> Result<String> {
    let host = hostname::get().context("cannot read the host name")?;
    Ok(format!("{}.local.", host.to_string_lossy()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_service_is_announced_with_its_type_and_port() {
        let service = service_info(7878).unwrap();

        assert_eq!(service.get_type(), SERVICE_TYPE);
        assert_eq!(service.get_port(), 7878);
    }
}
