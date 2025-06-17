#!/usr/bin/env python3
"""Click CLI for interacting with CAMI server API."""

import json
import sys
from typing import Optional

import click
import httpx

BASE_URL = "http://127.0.0.1:8000"


@click.group()
def cli():
    """CAMI CLI - Chat with your assistant via command line."""
    pass


@click.command()
@click.option("--thread", "-t", help="Use existing thread ID")
@click.option("--message", "-m", help="Send message directly without interactive mode")
@click.option(
    "--stream/--no-stream", default=True, help="Stream responses (default: True)"
)
def thread(thread: Optional[str], message: Optional[str], stream: bool):
    """Start a new thread or continue an existing one."""
    client = httpx.Client(base_url=BASE_URL)

    try:
        # Get or create thread
        if thread:
            # Use existing thread
            thread_id = thread
            click.echo(f"Using existing thread: {thread_id}")

            # Verify thread exists
            try:
                response = client.get(f"/api/v1/threads/{thread_id}")
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    click.echo(f"Thread {thread_id} not found. Creating a new one...")
                    thread_id = create_new_thread(client)
                else:
                    raise
        else:
            # Create new thread
            thread_id = create_new_thread(client)
            click.echo(f"Created new thread: {thread_id}")

        # Send message if provided
        if message:
            send_message_and_stream(client, thread_id, message, stream)
        else:
            # Interactive mode
            click.echo("Interactive mode - type your messages (Ctrl+C to exit)")
            try:
                while True:
                    user_message = click.prompt("You", type=str)
                    if user_message.lower() in ["exit", "quit", "bye"]:
                        break
                    send_message_and_stream(client, thread_id, user_message, stream)
            except KeyboardInterrupt:
                click.echo("\nGoodbye!")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        client.close()


def create_new_thread(client: httpx.Client) -> str:
    """Create a new thread and return its ID."""
    response = client.post("/api/v1/threads")
    response.raise_for_status()
    data = response.json()
    return data["thread_id"]


def send_message_and_stream(
    client: httpx.Client, thread_id: str, message: str, should_stream: bool
):
    """Send message to thread and optionally stream the response."""
    # Send message
    payload = {"message": message}
    response = client.post(f"/api/v1/threads/{thread_id}/run", json=payload)
    response.raise_for_status()

    if should_stream:
        click.echo("Assistant:", nl=False)
        stream_responses(thread_id)
    else:
        click.echo("Message sent successfully!")


def stream_responses(thread_id: str):
    """Stream responses from the thread using SSE."""
    url = f"{BASE_URL}/api/v1/threads/{thread_id}/responses/stream"

    try:
        with httpx.stream("GET", url, timeout=10.0) as response:
            response.raise_for_status()

            # Parse SSE manually since httpx.stream works differently
            buffer = ""
            message_received = False

            for chunk in response.iter_text():
                buffer += chunk
                while "\n\n" in buffer:
                    event_data, buffer = buffer.split("\n\n", 1)
                    if event_data.startswith("data: "):
                        data = event_data[6:]  # Remove "data: " prefix
                        if data.strip():
                            try:
                                parsed_data = json.loads(data)
                                if parsed_data.get("type") == "error":
                                    click.echo(
                                        f"\nError: {parsed_data.get('message')}",
                                        err=True,
                                    )
                                    return
                                elif parsed_data.get("event") == "message":
                                    # Extract and print only the data field
                                    content = parsed_data.get("data", "")
                                    if content:
                                        click.echo(f" {content}", nl=False)
                                        message_received = True
                                elif (
                                    parsed_data.get("event") == "done"
                                    or parsed_data.get("type") == "done"
                                ):
                                    # Response is complete
                                    break
                            except json.JSONDecodeError:
                                # Raw data, print as is
                                click.echo(f" {data}", nl=False)
                                message_received = True

                # Break after receiving a message to prevent hanging
                if message_received:
                    break

            click.echo()  # New line after streaming

    except httpx.TimeoutException:
        click.echo()  # Just new line, timeout is expected
    except httpx.HTTPStatusError as e:
        click.echo(f"\nStream error: {e}", err=True)
    except KeyboardInterrupt:
        click.echo("\nStream interrupted")
    except Exception as e:
        click.echo(f"\nStream error: {e}", err=True)


@click.command()
@click.argument("thread_id")
def info(thread_id: str):
    """Get information about a thread."""
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    try:
        response = client.get(f"/api/v1/threads/{thread_id}")
        response.raise_for_status()
        data = response.json()
        click.echo(f"Thread ID: {data['thread_id']}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            click.echo(f"Thread {thread_id} not found", err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        client.close()


# Add commands to the CLI group
cli.add_command(thread)
cli.add_command(info)


if __name__ == "__main__":
    cli()
