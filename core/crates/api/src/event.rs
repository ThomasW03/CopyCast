//! Messages pushed to clients over the WebSocket. Shapes are defined in `events.schema.json`.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum PlaybackStatus {
    Stopped,
    Playing,
    Paused,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum Event {
    #[serde(rename = "hello")]
    Hello { version: String },

    #[serde(rename = "playback.state")]
    PlaybackState {
        status: PlaybackStatus,
        item_id: Option<i64>,
        position_ms: u64,
        volume: u8,
    },

    #[serde(rename = "library.updated")]
    LibraryUpdated,

    #[serde(rename = "pairing.requested")]
    PairingRequested {
        request_id: String,
        device_name: String,
        code: String,
    },
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn hello_is_tagged_with_its_type() {
        let event = Event::Hello {
            version: "0.1.0".into(),
        };

        let value = serde_json::to_value(event).unwrap();

        assert_eq!(value, json!({ "type": "hello", "version": "0.1.0" }));
    }

    #[test]
    fn playback_state_uses_a_dotted_type_and_lowercase_status() {
        let event = Event::PlaybackState {
            status: PlaybackStatus::Playing,
            item_id: Some(1),
            position_ms: 83_000,
            volume: 60,
        };

        let value = serde_json::to_value(event).unwrap();

        assert_eq!(
            value,
            json!({
                "type": "playback.state",
                "status": "playing",
                "item_id": 1,
                "position_ms": 83000,
                "volume": 60
            })
        );
    }

    #[test]
    fn library_updated_carries_only_its_type() {
        let value = serde_json::to_value(Event::LibraryUpdated).unwrap();

        assert_eq!(value, json!({ "type": "library.updated" }));
    }
}
