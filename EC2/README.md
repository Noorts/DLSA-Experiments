## EC2 Instructions

- Connect to instance over ssh.
- Install rust - `curl https://sh.rustup.rs -sSf | sh`
- Install nightly - `rustup toolchain install nightly`
- Use nighty - `rustup default nightly`
- Install tools (for gcc) - `sudo yum groupinstall "Development Tools"`
- Run `RUSTFLAGS="-C target-cpu=native" PLATFORM=EC2/c5.large cargo run --release`