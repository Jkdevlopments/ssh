import asyncio
import asyncssh


class MySSHServerSession(asyncssh.SSHServerSession):

    def connection_made(self, chan):
        self._chan = chan
        print("[+] SSH shell connected")

    def shell_requested(self):
        print("[+] Shell requested")
        return True

    def exec_requested(self, command):
        print(f"[+] Command requested: {command}")

        self._chan.write(
            f"Command received: {command}\n"
        )

        self._chan.exit(0)

        return True

    def data_received(self, data, datatype):
        print(f"[CLIENT] {data}", end="")

        self._chan.write(data)

    def connection_lost(self, exc):
        if exc:
            print(f"[-] Shell error: {exc}")
        else:
            print("[-] SSH shell closed")


class MySSHServer(asyncssh.SSHServer):

    def connection_made(self, conn):
        peer = conn.get_extra_info("peername")

        if peer:
            print(
                f"[+] Incoming connection from "
                f"{peer[0]}:{peer[1]}"
            )

    def connection_lost(self, exc):

        if exc:
            print(f"[-] SSH connection lost: {exc}")
        else:
            print("[-] SSH connection closed")

    # -----------------------------
    # Authentication
    # -----------------------------

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):

        print(f"[*] Login attempt: {username}")

        if username == "admin" and password == "secret":
            print("[+] Authentication successful")
            return True

        print("[-] Authentication failed")
        return False

    # -----------------------------
    # SSH shell
    # -----------------------------

    def session_requested(self):

        print("[+] SSH session requested")

        # IMPORTANT:
        # Return session object, NOT True
        return MySSHServerSession()

    # -----------------------------
    # ssh -R
    # -----------------------------

    def server_requested(self, listen_host, listen_port):

        print("[+] Remote forwarding requested")
        print(f"    Listen host : {listen_host}")
        print(f"    Listen port : {listen_port}")

        # Allow remote port forwarding
        return True


async def main():

    print("[*] Starting SSH server...")

    await asyncssh.create_server(
        MySSHServer,
        host="0.0.0.0",
        port=2222,
        server_host_keys=["ssh_host_key"],
    )

    print("[+] SSH server listening on 0.0.0.0:2222")

    await asyncio.Future()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except (OSError, asyncssh.Error) as exc:
        print(f"[-] SSH server error: {exc}")
