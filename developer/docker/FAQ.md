Some problems that have been seen and their solutions.

## Postgres container dies shortly after starting it
#### Scenario
On the very first run, the postgres container will perform some initialization
steps. One of those steps is to ensure the data directory has proper
ownership and mode. If it can't do this, it will fail.

#### What to check
- Check logs for the postgres container
```
docker ps -a | grep postgres | cut -d' ' -f1 | xargs -r docker logs
```
- Check ownership of the local dir `./data/`

#### Possible causes
1. If the data dir on the local host is owned by root, the postgres container will
not be able to change permissions and will fail with a message inidicating so.

#### Possible resolutions
1. Update ownership of `./data/` to your local user



## Opensearch node containers die shortly after starting them
#### Scenario
As part of developer setup, containers exit after a few seconds of running.

#### What to check
- Check the logs for error messages to be resolved.
```
docker ps -a | grep -F 'opensearch-node' | head -1 | cut -d' ' -f1 | xargs -r docker logs
```

#### Possible causes
1. vm_max_map_count might be set too low.

#### Possible resolutions
1. Resolution is OS dependent.
  - Linux:
    - `sudo echo 'vm.max_map_count=262144' >>/etc/sysctl.d/local.conf`
    - `sudo sysctl --system`
    - `sudo sysctl vm.max_map_count`


## DB initialization throws lots of errors
#### Scenario
Running the script
```
./local_scripts/initialize_db.sh
```
results in lots of errors.

#### What to check
?
#### Possible Causes
? Unknown at this time
#### Possible resolutions
Some errors are (unfortunately) expected. Just try to start the server and see
if it works.
