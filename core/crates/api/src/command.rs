//! Commands a client can send to the player. Shapes are defined in `openapi.yaml`.

use serde::Deserialize;

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
pub enum PlaybackCommand {
    Play { item_id: i64 },
    Pause,
    Resume,
    Seek { position_ms: u64 },
    SetVolume { level: u8 },
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_a_command_selected_by_its_action() {
        let command: PlaybackCommand =
            serde_json::from_str(r#"{ "action": "seek", "position_ms": 5000 }"#).unwrap();

        assert_eq!(command, PlaybackCommand::Seek { position_ms: 5000 });
    }

    #[test]
    fn rejects_an_unknown_action() {
        let result = serde_json::from_str::<PlaybackCommand>(r#"{ "action": "explode" }"#);

        assert!(result.is_err());
    }
}
