FROM --platform=linux/x86_64 ubuntu:jammy
LABEL maintainer="Ben Chatterton <bchatterton@mozilla.com>"

# Add worker user
RUN mkdir /builds && \
    adduser --home /builds/worker --shell /bin/bash --disabled-password --gecos "" worker && \
    mkdir /builds/worker/artifacts && \
    chown worker:worker /builds/worker/artifacts && \
    chown worker:worker /root && \
    chmod u+w /root


# Update repositories
RUN apt update -y && apt upgrade -y

# Setup deps
RUN apt install -y git python3-pip python-is-python3 libasound2 pulseaudio && \
    apt install -y curl jq wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --no-cache --upgrade pip setuptools pytest selenium pipenv ruff

# %include-run-task

ENV PATH=/root/.local/bin:$PATH

ENV PATH=/root/.local/bin/firefox:$PATH

ENV SHELL=/bin/bash \
    HOME=/builds/worker \
    PATH=/builds/worker/.local/bin:/root/.local/bin:$PATH

ENV MOZ_LOG_FILE=/builds/worker/artifacts/fx_log
ENV MOZ_DISABLE_CONTENT_PROCESS=1
ENV MOZ_LOG=HTMLMediaElement:4,HTMLMediaElementEvents:4,cubeb:5,PlatformDecoderModule:5,AudioSink:5,AudioSinkWrapper:5,MediaDecoderStateMachine:4,MediaDecoder:4,MediaFormatReader:5,GMP:5,EME:5

RUN pactl list > /builds/worker/artifacts/pactl_list

VOLUME /builds/worker/checkouts
VOLUME /builds/worker/.cache

# Set a default command useful for debugging
CMD ["/bin/bash"]
