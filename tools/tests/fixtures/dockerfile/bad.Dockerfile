# Fixture: unpinned base image (DL3006) and apt-get without cleanup.
FROM debian
RUN apt-get update && apt-get install -y curl
