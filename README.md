# centos-rpm-odr-audioenc
CentOS 7 RPM Specfile for [Opendigitalradio's ODR-AudioEnc](https://github.com/Opendigitalradio/ODR-AudioEnc) which is part of [RaBe's DAB / DAB+ broadcasting package collection](https://build.opensuse.org/project/show/home:radiorabe:dab).

## Usage
There are pre-built binary packages for CentOS 7 available on [Radio RaBe's OBS DAB / DAB+ broadcasting package repository](https://build.opensuse.org/project/show/home:radiorabe:dab), which can be installed as follows:

```bash
curl -o /etc/yum.repos.d/home:radiorabe:dab.repo \
     http://download.opensuse.org/repositories/home:/radiorabe:/dab/CentOS_7/home:radiorabe:dab.repo
     
yum install odr-audioenc
```

### Running odr-audioenc through systemd
`odr-audioenc` can be started via the installed systemd service unit template
(and therefore supports multiple instances):
```bash
systemctl start odr-audioenc@<INSTANCE>.service

# To start an instance named "example":
systemctl start odr-audioenc@example.service

```

To start an `odr-audioenc` service on boot:
```bash
systemctl enable odr-audioenc@<INSTANCE>.service

# To start an instance named "example":
systemctl enable odr-audioenc@example.service

```

Status and logs of an `odr-audioenc` service instance:
```
systemctl status odr-audioenc@<INSTANCE>.service
journalctl -u odr-audioenc@<INSTANCE>.service

# Status and journal entries of an instance named "example"
systemctl status odr-audioenc@example.service
journalctl -u odr-audioenc@example.service
```


#### odr-audioenc parameter and options
The service uses an [ALSA](https://www.alsa-project.org) input and encodes to a
[ZeroMQ](http://zeromq.org/) via TCP (`tcp://localhost:9000`) output by
default.

All the default `odr-audioenc` command options and arguments can be overriden
by modifying the respective environment variables via the systemd service
[`Environment=`](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Environment=)
options (`Environment="AUDIOENC_*"`). The following options can be overriden (including their default values):
* `Environment="AUDIOENC_INPUT_OPTS=--device=default"`  
  Options controlling `odr-audioenc`'s input (`default` ALSA device)
* `Environment="AUDIOENC_ENCODER_BITRATE=64"`  
  Encoder output bitrate in kbits/s
* `Environment="AUDIOENC_ENCODER_CHANNELS=2"`  
  Number of input channels
* `Environment="AUDIOENC_ENCODER_SAMPLERATE=48000"`  
  Input sample rate in Hz
* `Environment="AUDIOENC_OUTPUT_OPTS=--output=tcp://localhost:9000"`  
  Options controlling `odr-audioenc`'s output
* `Environment="AUDIOENC_MISC_OPTS="`  
  Miscellaneous options and arguments to pass to `odr-audioenc`

To override the options, you can either interactively edit a service instance or
directly install an override file:
```bash
# Interactively edit and instance
systemctl edit odr-audioenc@<INSTANCE>.service

# Interactively edit the instance named "example":
systemctl enable odr-audioenc@example.service


# Install an override file
mkdir /etc/systemd/system/odr-audioenc@<INSTANCE>.service.d/

cat << EOF >> /etc/systemd/system/odr-audioenc@<INSTANCE>.service.d/override.conf
[Service]

# Change bitrate to 96 kbit/s
Environment="AUDIOENC_ENCODER_BITRATE=96"

# Include PAD data from odr-padenc
Environment="AUDIOENC_MISC_OPTS=--pad=6 --pad-fifo=/var/tmp/odr/padenc/%i/pad.fifo"
EOF
```

`systemctl cat odr-audioenc@.service` shows further (commented) override
examples.

#### odr-audioenc together with odr-padenc
From the previous override example, it can be seen, that an `odr-audioenc`
service unit instance plays nicely together with an
[`odr-padenc`](https://github.com/radiorabe/centos-rpm-odr-padenc#running-odr-padenc-through-systemd)
service unit instance. Simply create an `odr-audioenc` and `odr-padenc`
instance with the same instance name and they will use the same PAD data FIFO:
```bash
# Start the odr-padenc example instance
systemctl start odr-padenc@example.service
systemctl enable odr-padenc@example.service


# Enable PAD data via FIFO on the odr-audioenc example instance
mkdir /etc/systemd/system/odr-audioenc@example.service.d

cat << "EOF" >> /etc/systemd/system/odr-audioenc@example.service.d/override.conf
[Service]
Environment="AUDIOENC_MISC_OPTS=--pad=6 --pad-fifo=/var/tmp/odr/padenc/%i/pad.fifo"
EOF

# Start the odr-audioenc example instance
systemctl start odr-audioenc@example.service
systemctl enable odr-audioenc@default.service
```

An `odr-audioenc` service unit instance will be started after a potential
`odr-padenc` instance with the same instance name (`After=...
odr-padenc@%i.service`) during boot-up. This ensures that `odr-padenc` can
create the FIFO socket beforehand.
