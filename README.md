# CMD LC-1 Ableton 9 Control surface script
A port of the original Behringer control surface script to Ableton 9.1.4+.
Please report any bug using in the issue section.

## Installation notes
Read this first if you have troubles making it run. Please close Ableton before following this procedure.

- Download the latest script from [here](https://github.com/mpiraux/CMD-LC-1-Ableton-9-Control-Surface-Script/archive/master.zip).
- Go to Ableton's MIDI Remote Scripts directory. [Here](https://www.ableton.com/en/help/article/install-third-party-remote-script/) is how to find it.
  - Users have reported that, on Windows, the location `C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Script` worked while the other one found as indicated above didn't. 
- Create an empty directory named `CMD_LC1`, avoid using space or `-`. Ableton is pretty sensitive to directory names so I recommend you to use mine.
- Extract the downloaded zip, and copy all the `.py` files inside into the directory you've created.
- Start Ableton, you should be able to select the script appearing in the control surface list with the name of the directory previously created.

If this is not working, please fill in an [issue](https://github.com/mpiraux/CMD-LC-1-Ableton-9-Control-Surface-Script/issues) and provide your [Log.txt file](http://support.liine.net/customer/portal/articles/1339939-where-is-log-txt-) along with the description of you problem.

## Troubleshooting
**\#1:** I would like to use the script with another channel than Behringer default one.

  If you changed the channel of your device, you can simply make the script work again by changing a single value [here](https://github.com/mpiraux/CMD-LC-1-Ableton-9-Control-Surface-Script/blob/master/LC1.py#L40). The `CHANNEL` variable represents the MIDI channel of the device. Be careful though, because Behringer channel changer software labels channel from 1 to 16, but in fact MIDI channels are numbered from 0 to 15. So be sure to subtract your channel number by one when changing this variable.
  
**\#2:** I have two devices and I would like them to be independent.

  Simply duplicate the script directory, change one device channel and then change the duplicate script to match your channel. Read \#1 for more information about matching channels.
