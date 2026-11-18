mod common;

use std::time::Duration;

use common::{spawn_server, test_state};
use copycast_api::Event;
use futures_util::StreamExt;
use serde_json::{Value, json};
use tokio::net::TcpStream;
use tokio::time::timeout;
use tokio_tungstenite::tungstenite::Message;
use tokio_tungstenite::{MaybeTlsStream, WebSocketStream, connect_async};

type Client = WebSocketStream<MaybeTlsStream<TcpStream>>;

const WAIT: Duration = Duration::from_secs(5);

async fn connect(address: std::net::SocketAddr) -> Client {
    let url = format!("ws://{address}/api/v1/ws");
    let (client, _) = connect_async(url).await.expect("websocket connects");
    client
}

async fn next_event(client: &mut Client) -> Value {
    let message = timeout(WAIT, client.next())
        .await
        .expect("an event arrives in time")
        .expect("the connection stays open")
        .expect("the message is valid");
    let Message::Text(text) = message else {
        panic!("expected a text message");
    };
    serde_json::from_str(text.as_str()).expect("the message is JSON")
}

#[tokio::test]
async fn a_new_client_receives_a_hello() {
    let address = spawn_server(test_state().await).await;
    let mut client = connect(address).await;

    let hello = next_event(&mut client).await;

    assert_eq!(
        hello,
        json!({ "type": "hello", "version": env!("CARGO_PKG_VERSION") })
    );
}

#[tokio::test]
async fn published_events_reach_the_client() {
    let state = test_state().await;
    let address = spawn_server(state.clone()).await;
    let mut client = connect(address).await;
    next_event(&mut client).await;

    state.events.publish(Event::LibraryUpdated);

    assert_eq!(
        next_event(&mut client).await,
        json!({ "type": "library.updated" })
    );
}
