# twitch2slack
twitchq is used to notify a Slack-channel when a Twitch channel go online/offline. Polls Twitch API every 60s.
Comes in 2 flavors: Service and one-time-run.


##twitchq_service.py:
Service is just a while loop which does stuff and then sleep for 60s.

Pros:
* Can be run in the background.
* Logs to log file for error handling.
* Runs in memory.

Cons:
* Some kind of process overwatch is required in case it crashes.
* Runs in memory. Stream status is lost if script crash.
* Untested for any memory leaks.

##twitchq_otr.py:
OTR run once and then exits.

Pros:
* Can be run on demand.
* Persistent storage on stream status.

Cons:
* Use disk writes to save stream status.
* Task scheduling required if automatic notifies is wanted.
* No logging (yet).

# Requirements
* Python 3
* External Python 3 modules
  * dateutil
  * pytz
  * requests
  * [twitchchannelquery](https://github.com/Luppii/twitchquery)

# Installing
1. Install Python 3 and pip.

1. Install following Python 3 modules (pip install):
   * dateutil
   * pytz
   * requests

1. Make sure twitchchannelquery module is in the same dir as twitchq.

1. Run twitchq (flavor of your choice) to generate the file 'config.json'.
   Exit script (if running service) and modify this file with your own settings.

1. Choose twitchq flavor.
   * OTR: Setup a cron job to run at regular intervals.
   * Service: Configure some kind of process overwatch to restart script
     just in case it dies.
