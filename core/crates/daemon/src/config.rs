//! Command-line and environment configuration.

use std::net::{IpAddr, Ipv4Addr, SocketAddr};
use std::path::PathBuf;

use clap::Parser;
use directories::ProjectDirs;

const DEFAULT_PORT: u16 = 7878;
const DATABASE_FILE: &str = "copycast.db";

#[derive(Debug, Clone, Parser)]
#[command(version, about = "The CopyCast daemon")]
pub struct Config {
    /// Address the control API listens on. The default only accepts connections from this
    /// machine; use 0.0.0.0 to let paired phones on the local network connect.
    #[arg(long, env = "COPYCAST_HOST", default_value_t = IpAddr::V4(Ipv4Addr::LOCALHOST))]
    pub host: IpAddr,

    /// TCP port of the control API.
    #[arg(long, env = "COPYCAST_PORT", default_value_t = DEFAULT_PORT)]
    pub port: u16,

    /// Directory holding the database and the caches.
    #[arg(long, env = "COPYCAST_DATA_DIR", default_value_os_t = default_data_dir())]
    pub data_dir: PathBuf,
}

impl Config {
    pub fn address(&self) -> SocketAddr {
        SocketAddr::new(self.host, self.port)
    }

    pub fn database_path(&self) -> PathBuf {
        self.data_dir.join(DATABASE_FILE)
    }

    /// Whether other devices of the local network can reach the daemon.
    pub fn is_exposed(&self) -> bool {
        !self.host.is_loopback()
    }
}

fn default_data_dir() -> PathBuf {
    ProjectDirs::from("org", "copycast", "CopyCast")
        .map(|dirs| dirs.data_dir().to_path_buf())
        .unwrap_or_else(|| PathBuf::from("data"))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse(arguments: &[&str]) -> Config {
        let program = ["copycast-daemon"];
        Config::try_parse_from(program.iter().chain(arguments)).unwrap()
    }

    #[test]
    fn listens_on_localhost_by_default() {
        let config = parse(&[]);

        assert_eq!(config.address(), "127.0.0.1:7878".parse().unwrap());
        assert!(!config.is_exposed());
    }

    #[test]
    fn the_host_and_port_can_be_overridden() {
        let config = parse(&["--host", "0.0.0.0", "--port", "9000"]);

        assert_eq!(config.address(), "0.0.0.0:9000".parse().unwrap());
        assert!(config.is_exposed());
    }

    #[test]
    fn the_database_lives_in_the_data_directory() {
        let config = parse(&["--data-dir", "/tmp/copycast"]);

        assert_eq!(
            config.database_path(),
            PathBuf::from("/tmp/copycast").join("copycast.db")
        );
    }
}
