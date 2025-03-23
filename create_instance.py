from openstack import connection, compute, enable_logging
import sys

enable_logging(debug=True)

def get_connection():
    try:
        conn = connection.Connection(cloud='openstack')
        for server in compute.v2.server.Server.list(session=conn.compute):
            print(server.to_dict())
        print("Authenticated successfully.\n")
        return conn
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        sys.exit(1)

def main():
    conn = get_connection()

    print("--- Create Instance ---")
    server_name = input("Instance Name: ").strip()
    image_id = input("Image ID (UUID): ").strip()
    flavor_id = input("Flavor ID (UUID): ").strip()
    network_id = input("Network ID (UUID): ").strip()

    if not all([server_name, image_id, flavor_id, network_id]):
        print("Error: All fields are required.")
        sys.exit(1)

    try:
        print("Verifying resources...")
        image = conn.compute.find_image(image_id)
        flavor = conn.compute.find_flavor(flavor_id)
        network = conn.network.find_network(network_id)

        if not image:
            print(f"Image not found: {image_id}")
            sys.exit(1)
        if not flavor:
            print(f"Flavor not found: {flavor_id}")
            sys.exit(1)
        if not network:
            print(f"Network not found: {network_id}")
            sys.exit(1)

        print("Creating instance...")
        server = conn.compute.create_server(
            name=server_name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}]
        )

        print("Waiting for server to become ACTIVE...")
        server = conn.compute.wait_for_server(server)

        print(f"\nInstance '{server.name}' created successfully.")
        print(f"ID: {server.id}")
        print(f"Status: {server.status}")

    except Exception as e:
        print(f"Error creating server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
