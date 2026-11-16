//! `GET /ws`: streams events to a client.

use axum::Router;
use axum::extract::State;
use axum::extract::ws::{Message, WebSocket, WebSocketUpgrade};
use axum::response::Response;
use axum::routing::get;
use tokio::sync::broadcast::Receiver;
use tokio::sync::broadcast::error::RecvError;

use crate::VERSION;
use crate::event::Event;
use crate::state::AppState;

pub fn routes() -> Router<AppState> {
    Router::new().route("/ws", get(upgrade))
}

async fn upgrade(upgrade: WebSocketUpgrade, State(state): State<AppState>) -> Response {
    // Subscribing before the upgrade completes means no event is missed after the greeting.
    let events = state.events.subscribe();
    upgrade.on_upgrade(|socket| serve_client(socket, events))
}

async fn serve_client(mut socket: WebSocket, mut events: Receiver<Event>) {
    let hello = Event::Hello {
        version: VERSION.to_owned(),
    };
    if send_event(&mut socket, &hello).await.is_err() {
        return;
    }
    forward_events(&mut socket, &mut events).await;
}

async fn forward_events(socket: &mut WebSocket, events: &mut Receiver<Event>) {
    loop {
        tokio::select! {
            received = events.recv() => {
                if !relay(socket, received).await {
                    break;
                }
            }
            message = socket.recv() => {
                if client_has_left(&message) {
                    break;
                }
            }
        }
    }
}

/// Sends one received event to the client. Returns `false` when the connection should end.
async fn relay(socket: &mut WebSocket, received: Result<Event, RecvError>) -> bool {
    match received {
        Ok(event) => send_event(socket, &event).await.is_ok(),
        Err(RecvError::Lagged(skipped)) => {
            tracing::warn!(skipped, "client too slow, some events were dropped");
            true
        }
        Err(RecvError::Closed) => false,
    }
}

fn client_has_left(message: &Option<Result<Message, axum::Error>>) -> bool {
    matches!(message, None | Some(Err(_)) | Some(Ok(Message::Close(_))))
}

async fn send_event(socket: &mut WebSocket, event: &Event) -> Result<(), axum::Error> {
    let json = serde_json::to_string(event).map_err(axum::Error::new)?;
    socket.send(Message::text(json)).await
}
