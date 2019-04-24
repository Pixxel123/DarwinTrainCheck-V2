# DarwinTrainCheck

This is a project made for tracking the trains on my commute after dealing with numerous delays and cancellations.

Using a Python backend, it accesses the UK National Rail Live Departure Board SOAP API via Huxley, a JSON proxy, making it much easier to parse the data. This is then pushed via Flask to a Heroku instance.

The Heroku address takes parameters in the URL: the origin station (as CRS codes e.g. ECR, LBG, VIC, etc), the destination station and the times to look up (via a comma delimited string e.g. 1234,1255).

This data is then pushed to my phone via the Android app Tasker, which creates notifications at user specified time ranges, with minimum intervals of 2 minutes. The notification will change depending on the train statuses:

* If the trains are on time a silent notification will show as `Trains on Time (ECR - LBG)` with the service information as `12:34 (On time) | 12:55 (On time)` 

* If trains are delayed, the notification will vibrate in a specific pattern while showing as `Trains Late (ECR - LBG)` with the following service information `12:34 -> 12:47 | 12:55 (On time)`

*  If trains are cancelled, a different vibration pattern plays and the notification shows `Trains Cancelled (ECR -LBG)` and `12:34 (Cancelled) Previous service: 12:15 | 12:55 (On time)`

Both Late and Cancelled notifications have a Mute and Unmute toggle that gets reset each day to Mute, in case there are issues.
