# Defines the tag for OBS and build script builds:
#!BuildTag: sugar
# Use the repositories defined in OBS for installing packages
#!UseOBSRepositories
FROM	opensuse/tumbleweed

RUN	zypper -n install -y --no-recommends \
		python3 \
		python3-paramiko \
		python3-pyramid && \
	zypper -n clean -a

COPY	*.py /

ENV     PYTHONPATH /
ENV	PYTHONUNBUFFERED 1

EXPOSE	9999

ENTRYPOINT ["/usr/bin/python3", "/server.py"]
