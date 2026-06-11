if __name__ == "__main__":
    with open(".github/workflows/main.yml") as fh:
        config = fh.read()

    config = config.replace("smoke", "nightly-as-beta")
    with open(".github/workflows/main.yml") as fh:
        fh.write(config)
