# Image contract

What a container image needs to be deployable by this hosting platform,
what the platform adapts to, and what it guarantees in return.

**Audience:** whoever builds or picks an image — working in another
repository, without this platform's specification. This document
therefore states its own reasons and stands alone.

**How to read it.** The platform runs each instance as one Docker
container supervised by a host systemd unit. It **deploys and operates;
it never builds.** It carries the knowledge of the software it runs —
where it writes, how to talk to it, how to ask it to save — so that
adapting to an image is the platform's job wherever it can be.
Section 1 is the short list of what it genuinely cannot work around.
Everything after it is a **default with an escape hatch**: what happens
if you say nothing, and what to tell us if your image works
differently.

That distinction matters most when adopting an image someone else
built (§9). Very little below requires a purpose-built image.

---

## 1. The short list

Seven things, each with the reason it cannot be worked around:

1. **It runs as a uid and gid chosen at deploy time**, not baked in —
   that is what stops two instances on one host reading each other's
   saves (§2).
2. **Files the image ships are readable by that uid** — the platform
   will not chown a multi-gigabyte game directory into a new layer
   (§2.5).
3. **Everything worth keeping is written under paths the platform
   mounts**, and the image tells us which paths those are (§3).
4. **No secret is baked into the image**; secrets are read at start
   (§6).
5. **A stop request means save and exit**, within the stop grace
   period — the only requirement here whose violation is silent rather
   than immediate (§7).
6. **The tag says which version is inside** (§8).
7. **There is some way to ask whether the server is serving, and to ask
   it to save** — which way is agreed per image, and the platform holds
   that knowledge (§5).

Everything else is negotiable. If an item below does not fit your
image, the answer is usually a line on the per-image sheet (§11.2), not
a change to your image.

---

## 2. The uid, the gid, and the user

The platform runs each instance under an explicit numeric uid and gid,
unique per instance, from a range reserved for them (70000–70999). Two
instances on one host are isolated by owning different numbers over
owner-only directories.

**2.1 At build time, do not tie anything to a fixed uid.** Whatever
users the image declares is its own business — the platform overrides
the user when it starts the container, so a `USER` line is simply
ignored. What does not survive is *content* bound to a number: files
chowned at build time to a uid the process will not have (§2.5). The
number is chosen per instance at deploy, and changing it must never need
a rebuild.

**2.2 If your image has a `/etc/passwd`, the instance's uid has a name
in it — you never have to handle one that does not.** At deploy the
platform reads `/etc/passwd` and `/etc/group` **out of your image**,
appends one entry for the instance's uid and gid, and mounts the result
read-only. Your own users — `root`, `nobody`, whatever a package
created — are preserved, because they come from your image; exactly one
line is added. Nothing to request, nothing to build for, and
`getpwuid()` works.

The platform does this for every such image rather than on request,
because an accommodation used only in rare cases is one that breaks the
first time it is needed — and some runtimes do not tolerate an unnamed
uid at all.

**If your image ships no `/etc/passwd`, the platform adds none.** An
image built on `scratch` around a static binary was built not to need
one, and inventing a file it never had would be a change it did not ask
for. If such an image does turn out to need an entry, it is a line in
the sheet of §11.2 and the platform supplies one.

**2.3 If your image manages its own users, say so and the platform
stays out of the way.** Some entrypoints create the user themselves and
drop privileges, which is supported: no mounted `passwd`, no user set by
the platform, the uid and gid passed instead under the variable names
your image documents (§11.1), and the container started as root with
`no-new-privileges` and dropped capabilities. It is second choice for one reason only — the process is
root until it drops, and this section exists to keep it from ever being
root. With §2.2 in place, few images should need this.

**2.4 The home directory.** The platform sets `$HOME` to a writable path
it mounts and puts the same path in the `passwd` entry, so both agree.
If your image needs the home directory at a fixed path instead, tell us
the path and we mount it there.

**2.5 Files the image ships must be readable by any uid** — 0644 files,
0755 directories and executables. The platform never changes their
ownership: on a game image that is several gigabytes duplicated into a
new layer for no benefit. An image whose game files are `0750
root:root` meets every other line of this contract and then fails to
start.

---

## 3. Where the instance writes

Per instance the platform maintains one host directory for data and one
for rendered configuration. The data directory is what gets backed up,
restored and cloned, so what lands in it is what survives.

**3.1 Tell us where your image writes.** Saves, worlds, databases,
caches, logs it insists on writing, a home directory, a state file in an
odd place — list the paths. The platform mounts subdirectories of the
instance's data directory at each of them. You do not have to relocate
anything, and there is no single path your image must adopt.

**3.2 Anything not on that list is ephemeral.** It is not backed up and
does not survive a redeploy. That is fine for caches and temporary
files; it is a data-loss bug if a save lands there, which is why the
list matters more than where the paths are.

**3.3 `/tmp` is writable** and never preserved.

**3.4 Logs go to stdout and stderr.** The container runtime collects and
rotates them there. A log file inside the data path is backed up nightly
for no reason; outside it, it is lost and unrotated. If your image can
only log to a file, name the path under §3.1 and we will mount it
somewhere sane.

**3.5 Do not persist a secret you were given** into a mounted path or
the log stream — both the data and configuration directories are backed
up off-site. The platform may itself render a secret into the
configuration file where the software requires one (§6.3); that is its
decision to make, not something for the image to reproduce elsewhere.

---

## 4. Configuration

Two layers, deliberately: values that must match the runtime are passed
in, and everything else lives in a file the platform renders per
instance from its own template. Keeping the bulk in a file keeps each
server's configuration reviewable as a diff instead of growing the
environment surface without limit.

**4.1 Tell us where your image reads its configuration, and the
platform mounts it there.** A single file, several files, a whole
directory — whatever the software already expects, at the path it
already expects it. There is nothing for the image to look up and no
path convention to adopt.

**4.2 The rendered file is the platform's.** It is re-rendered on every
deploy and overwrites what is there, so a change is a reviewed diff
rather than a mystery. The image should not need write access to it.

**4.3 If the software rewrites its own configuration** — an in-game
admin panel writing back to it, for instance — tell us. It is not
forbidden; the platform then renders that file only when it is absent.
Left unsaid, every deploy silently reverts settings changed in game,
which is a baffling failure to debug from the other side.

**4.4 Memory.** The container runs under a hard memory limit. Where the
runtime has its own heap setting, the platform passes it under the
variable name your image documents, and it must end up **below** the
container limit — a
heap equal to the limit means the kernel's out-of-memory killer fires at
exactly the moment the garbage collector would have recovered.

---

## 5. Talking to a running server

The platform needs four things from a running game instance. **How** it
gets them is agreed per image and recorded on the sheet of §11.2, and
the platform carries the code:

| It needs to know | Why |
|---|---|
| whether the server is actually serving | The probe is the game, not the container. A process that is alive but has stopped answering is the common failure, and process state calls it healthy |
| how many players are connected | So a scheduled restart can skip the countdown when nobody is there |
| how to announce a message | Countdown before a scheduled stop, and the return afterwards |
| how to make it save, and know the save finished | The maintenance run stops the server immediately after. A save that returns early makes a cold backup no better than a hot one |

**5.1 Any of these mechanisms will do**, in rough order of how little
work they cost:

- a **query protocol on a port** — the Steam query protocol for Steam
  games, which answers "serving" and the player count in one call;
- an **admin protocol on a port** — RCON and its relatives, for
  announce and save;
- a **command run inside the container**, if the software has a console
  or a CLI rather than a socket. The platform can execute it in the
  running container; nothing has to listen, which is strictly safer;
- an **HTTP endpoint**, which is what application instances use;
- for liveness only, **a line in the log stream** the platform can match.

**5.2 A port-based admin interface is published on loopback only** and
must never be advertised to a server browser. The maintenance run
executes on the same host and reaches it locally. Nothing else has any
business reaching it — and not listening beats filtering.

**5.3 Answer honestly about readiness.** Whatever the mechanism, it must
not report the server as serving while a world is still loading, and
must stop reporting it once the server can no longer accept players.
Reporting too early lifts the maintenance alert suppression before the
server is back; reporting while dead defeats the probe entirely.

**5.4 Each mechanism is learnt once, on the platform side.** It speaks
the Steam query protocol and RCON today. Software with a protocol it
does not yet know is supported by teaching it that protocol — a change
to agree before the instance is declared, not something the image
should work around or reimplement.

### 5.5 The maintenance sequence, for context

So the requirements above have a shape. On every scheduled window, on
the instance's own host, with no dependency on any other machine:

1. Count the players.
2. Unless the server is empty and the instance allows skipping, announce
   at each countdown interval.
3. Ask for a save and wait for it to finish.
4. Stop the container, respecting the stop grace period.
5. If the window backs up: back up the data directory and verify the
   snapshot. A failed or unverified backup aborts before the restart.
6. Start the container again.
7. Announce the return, once the server reports it is serving.

---

## 6. Secrets

**6.1 Default: environment variables** — under the names your image
documents (§11.1), and no others. They come from a file owned by root
with owner-only permissions, handed to the container runtime when the
unit starts — never on a command line, never in the unit file, and not
in the unit's own environment either, where anyone able to ask systemd
about the service would be shown them. If your image only reads secrets
from files, say so and the platform writes them to a path you name
instead.

**6.2 The image holds none of them** and reads them at start. There is
no build-time secret and no default to fall back on: a missing secret
should be a fatal start, not a warning. This matters because the image
may be public — and a secret deleted in a later layer is still in the
earlier one.

**6.3 Where the software wants a secret as a configuration setting.**
Many game servers keep the admin and join passwords in the same file as
everything else, and some give no choice at all. Two ways, in order of
preference:

- **The image reads the value from its environment and injects it
  itself** — typically by copying the rendered file to `/tmp`,
  substituting, and starting the software against the copy. Preferred,
  because the value then exists only in the process's environment and
  memory, and never on disk.
- **The platform renders it into the configuration file** at deploy,
  from a placeholder in the template. Supported without argument where
  the software requires it — recommending against something is not the
  same as forbidding it, and an image should not have to be rebuilt
  around our preference. The file is then owned by the instance's uid
  with mode 0600, inside the instance's owner-only configuration
  directory: readable by that instance's process and by nothing else on
  the host. That is the same protection the instance's own saves get.

**What is absolute either way: the value never exists in the
repository.** The declaration holds no secret, the template holds a
placeholder, and the value is fetched from the secret store at deploy
time. That is the rule that actually matters. Where the secret sits on
the node afterwards is a question of degree — and a process that must
read its own password cannot be prevented from reading its own
password.

Two consequences of the second way, stated plainly rather than
discovered: the configuration directory is backed up, so the value
travels into the backup repository, which is encrypted — acceptable, not
free. And deploy never prints a configuration diff for such an instance.

**6.4 A secret must never reach stdout, stderr, a config dump or a crash
report.** Redact it if it must be mentioned at all.

---

## 7. Shutdown

**This is the requirement whose violation is silent.** Everything else
here fails immediately and visibly — a missing variable, an unreadable
path, a refused port. A shutdown that does not finish in time produces a
corrupted save days later, with nothing in any log to explain it.

**7.1 The platform sends the agreed stop signal to the container's main
process** — `SIGTERM` unless your image declares another one, in which
case the platform sends that — and waits the instance's full stop grace
period before `SIGKILL`. That process is PID 1 inside the container's
own process namespace: the container runtime arranges it and the image
has nothing to set up. But
PID 1 is not an ordinary process, and two consequences of that catch
images out.

**A signal PID 1 has no handler for is discarded by the kernel.** An
ordinary process is terminated by the stop signal by default; PID 1 is
not — the kernel delivers it only signals the process has explicitly
handled. So a server that installs no handler for it does not stop, runs
until the grace period expires, and is then killed with `SIGKILL` —
mid-write, every single time, with nothing in any log. Handling the stop
signal is the requirement; being PID 1 is why the default behaviour is
not enough.
(`SIGKILL` always lands: the kernel forces it from the parent namespace,
which is exactly why the grace period is the last line of defence and
not a formality.)

**A shell between the runtime and the server swallows the stop.**
`ENTRYPOINT server` is wrapped in `/bin/sh -c`, so the shell is PID 1 —
it neither handles the signal nor passes it on. Use the exec form,
`ENTRYPOINT ["server"]`, or `exec` the server from your entrypoint
script so it replaces the shell rather than parenting it.

If the image spawns children it does not reap, the platform can run it
under an init process that reaps and forwards signals — a per-instance
setting, no change to the image.

**7.2 On that signal, save and exit cleanly.** The grace period is
generous on purpose — ninety seconds is the starting point for a game
server — because the container runtime's own ten-second default sends an
uncatchable kill in the middle of a write. If your server needs longer,
say how long; it is a per-instance number.

**7.3 Exit zero when asked to stop, non-zero when it fails.** The unit
restarts a *failed* instance a few times and then leaves it stopped so
the alert fires — that is the signal supervision exists to give. A
requested stop is never restarted, so exiting non-zero on one does not
loop; it leaves the unit marked failed after every clean maintenance
window. Supervision then cries wolf on a healthy server, and an alert
channel that cries wolf is the one thing that makes a real failure go
unnoticed.

---

## 8. Publication and versioning

**8.1 Published to a public registry** — GHCR or Docker Hub. A private
image works but costs a pull credential on every node that runs the
instance, so public is simpler where the content allows it.

**8.2 The tag carries the version of what is inside** — the game
version, the application version. It is how an operator reads, from a
one-line declaration, what is running.

**8.3 The platform pins tag and digest, and runs the digest.** The tag
is documentation; the digest is what is pulled. So publishing new
content does not deploy it — the platform moves only when its
declaration is edited, which is the point: a re-pull must never
substitute a rebuilt image behind an unchanged tag. And moving a tag to
new content achieves nothing here while misleading everyone reading the
declaration, because nothing consults the tag. New content, new tag.

**8.4 The digest always exists**, including for an image you did not
build: it is the hash of the manifest, which is how every registry
stores an image. Read it without pulling with
`docker buildx imagetools inspect <ref>`, `skopeo inspect docker://<ref>`
or `crane digest <ref>`; after a pull,
`docker inspect --format '{{index .RepoDigests 0}}' <ref>`.

Two things to get right when recording one. A tag usually points at a
**manifest index** with one entry per architecture — pin the index
digest, which is what those commands return, and the runtime still
selects the right architecture; pinning an individual architecture's
manifest works but freezes it. And a digest is **meaningful only with
its repository**: `registry/repo@sha256:…`. Copying an image to another
registry can change it, so re-read it at the destination rather than
carrying the old value across.

---

## 9. Adopting an image you did not build

Most of this document is satisfiable without touching someone else's
image. In practice:

| Concern | Usually solved by |
|---|---|
| It writes in unexpected places | Listing those paths (§3.1) — the platform mounts them |
| It expects config at a fixed path | Mounting the rendered file there (§4.1) |
| It hardcodes its internal ports | Publishing host ports onto them (§10.2) |
| It wants a named user | Nothing — the platform already gives every instance's uid a name, built from your image's own `/etc/passwd` (§2.2) |
| It only reads secrets from files | Writing them to a path you name (§6.1) |
| Its console is a command, not a socket | Running that command in the container (§5.1) |

What genuinely cannot be worked around, and rules an image out until it
is fixed upstream: files unreadable by a non-root uid (§2.5), a hard
requirement to run as root, secrets baked into a layer, and a server
that cannot shut down cleanly on its stop signal.

---

## 10. What the platform guarantees

The obligations run both ways.

**10.1 Before the container starts:** every mounted path exists, owned
by the instance's uid and gid and readable and writable only by them;
the rendered configuration is in place; wherever the image ships a
`passwd` and `group` pair, the instance's uid and gid have a name in it
(§2.2); the variables of §11.1 that apply are set, secrets included;
`/tmp` is writable.

**10.2 Ports.** The platform decides the host ports per instance —
several instances share a host — and publishes each on exactly one host
interface: public for the ports players connect to, loopback for admin
ports. It passes them under the variable names your image
documents, for images that take their ports from the environment, and
maps them onto fixed container ports for images that do not. One caveat decides which: **a protocol
that advertises its own port** — a Steam server browser registration,
for instance — breaks if the container's port differs from the published
one, so those games must take their ports from the environment. Inside
the container, listen on `0.0.0.0`; the network namespace is not shared
with anything else, and binding narrower stops the publication working.

**10.3 On stop:** the agreed stop signal to the main process and the
instance's full
grace period before anything harsher.

**10.4 On the data:** backed up on the instance's schedule and restored
to the same ownership.

**10.5 What it will not do:** restart a running instance to apply a
configuration change without an announced stop; replace a running
instance's image behind its back; or touch the contents of the data
directory while the instance runs or as a side effect of a routine
deploy. That last has three deliberate exceptions, all operator actions
on a stopped instance: **restore** writes the data directory from a
snapshot, **clone** populates a new instance's empty data directory from
another's, and a first deploy onto a freshly created host restores the
latest snapshot rather than starting empty. All three re-own what they
write.

---

## 11. Reference

### 11.1 Variables the platform sets

**The variables your image documents are the ones it gets.** Tell us
what your README calls them — `RCON_PASSWORD`, `SERVER_PORT`, `PUID`,
`PGID`, `JAVA_OPTS` — and each instance's declaration names the platform
value to put in each: the secret it fetched, the port it allocated, the
uid it chose, the heap it decided. You rename nothing inside your image
to run here, and the declaration holds the *name* of the value, never
the value itself.

**The platform invents no names of its own beside them.** A variable
nothing reads is surface without a reader, and every value it has to
offer is one a declaration can ask for by name. If your image is built
for this platform and would rather read `INSTANCE_PORT_GAME`, that works
the same way — it is simply the name the declaration gives.

One exception, because it is not a value with a name:

| Variable | When | Meaning |
|---|---|---|
| `HOME` | always | Writable home directory, matching the `passwd` entry the platform generates (§2.4) — the two have to agree, so the platform sets both |

### 11.2 The per-image sheet

Every default in this document can be varied per image, and the varying
is written down rather than remembered. Before an image is built or
adopted, the platform team and whoever owns the image agree a short
sheet covering:

| Line | What it settles |
|---|---|
| Ports | Which port roles the software needs and the variable name it reads each from; or that it takes fixed ports the platform maps onto (§10.2). Two roles may name one number where one listener serves both purposes |
| Secrets | Which secrets the software needs, the variable name it reads each one from, and whether the image injects it or the platform renders it into the configuration (§6.3) |
| Writable paths | Where the software writes, so the platform mounts there (§3.1) |
| Configuration | Where it reads its configuration, and whether it rewrites it (§4.1, §4.3) |
| Serving and players | How the platform asks whether the server is up and how many are connected (§5.1) |
| Announce and save | How the platform announces and triggers a save (§5.1) |
| Stop signal and grace period | Which signal means "shut down" if not `SIGTERM`, and how long a clean shutdown needs (§7.1, §7.2) |
| Identity | Whether the image manages its own users, and whether it needs a `passwd` entry it does not ship (§2.2, §2.3) |

Nothing on that sheet requires anything of the image: each line records
what the image already does, so the platform can accommodate it. A line
left open is not an oversight — it is a question to answer before the
first deployment rather than during it.

---

## 12. Changing this contract

This document and the platform move together. When the platform changes
what it needs from an image, this file changes in the same commit —
otherwise the two projects drift apart and the next deploy fails for
reasons neither repository explains.

The reverse holds more often, and is the normal case rather than an
exception: an image that works differently from a default here is a line
on the sheet of §11.2, agreed before it is deployed. The only bad
outcome is
finding out at deploy time.
