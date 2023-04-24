import zhinst,re

def parasetting(device_id,label_labone,channel,voltage,frequency,bindwidth):
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session(device_id, apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    channel_adc = 0
    if re.search("电流", channel):
        channel_adc = 1
    elif(re.search("电压", channel)):
        channel_adc = 0
    exp_setting = [
    ["/%s/oscs/%d/freq" % (labone, 0), frequency],
    ["/%s/demods/%d/adcselect" % (labone, 0), channel_adc],
    ["/%s/demods/%d/bindwidth" % (labone, 0), bindwidth],
    ["/%s/sigouts/%d/amplitudes/%d" % (labone, 0, 0),voltage,],]
    daq.set(exp_setting)
    daq.sync()