//! In-process fan-out of events to every connected WebSocket client.

use tokio::sync::broadcast;

use crate::Event;

/// Events a slow client may fall behind by before it starts missing some.
const CAPACITY: usize = 64;

#[derive(Debug, Clone)]
pub struct EventBus {
    sender: broadcast::Sender<Event>,
}

impl EventBus {
    pub fn new() -> Self {
        let (sender, _) = broadcast::channel(CAPACITY);
        Self { sender }
    }

    /// Sends the event to every subscriber. Having no subscriber is not an error.
    pub fn publish(&self, event: Event) {
        let _ = self.sender.send(event);
    }

    pub fn subscribe(&self) -> broadcast::Receiver<Event> {
        self.sender.subscribe()
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn subscribers_receive_published_events() {
        let bus = EventBus::new();
        let mut receiver = bus.subscribe();

        bus.publish(Event::LibraryUpdated);

        assert_eq!(receiver.recv().await.unwrap(), Event::LibraryUpdated);
    }

    #[test]
    fn publishing_without_subscribers_does_not_fail() {
        EventBus::new().publish(Event::LibraryUpdated);
    }
}
