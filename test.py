import zhinst.utils
hf2 = False
apilevel_example = 1 if hf2 else 6
(daq, labone, props) = zhinst.utils.create_api_session("dev4346", apilevel_example, server_host="localhost", server_port=8004)
zhinst.utils.api_server_version_check(daq)
pid_Mode = daq.get('/%s/pids/%d/mode'%(labone,0)) # pid模式
print(pid_Mode["dev4346"]["pids"]["0"]["mode"]["value"][0])
pid_Shift = daq.get('/%s/pids/%d/shift'%(labone,0)) # pid shift
print(pid_Shift["dev4346"]["pids"]["0"]["shift"]["value"][0])
pid_Setpoint = daq.get('/%s/pids/%d/setpoint'%(labone,0)) # pid setpoint
print(pid_Setpoint["dev4346"]["pids"]["0"]["setpoint"]["value"][0])
data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
print(data)
print(data['x'][0])
print(data['y'][0])
print(data['frequency'][0])
print(data['phase'][0])
vol_data = daq.get('/%s/auxouts/%d/value'%(labone,0)) # pid auouts
vol = vol_data["dev4346"]["auxouts"]["0"]["value"]["value"][0]
print(vol)