import time
# import data and build arrays and dictionaries to store data
f = open('connect_dict.txt', 'r')
connect_dict = eval(f.read())
f.close()
FlightDelay = dict()
with open('connecting.txt','r') as f:
	for line in f:
		if not '[' in line:
			pass
		else:
			name, element = line.split('[')
			name = name.strip()
			name = name.strip('"')
			name = name.split()[0]+' '+name.split()[1]+' '+name.split()[2]+' '+name.split()[4]+name.split()[6]
			element = element.strip(']')
			DepDelay, ArrDelay = element.split(',')
			DepDelay = DepDelay.strip(']')
			ArrDelay = ArrDelay.strip()
			ArrDelay = ArrDelay.strip(']')
			FlightDelay[name] = (DepDelay, ArrDelay)
airports = []
with open('airports.txt','r') as f:
	for line in f:
		airport = line.split('"')[1]
		airports.append(airport)
flights = dict()
with open('timelist.txt','r') as f:
	for line in f:
		line = line.strip()
		flight = line.split('"')[1]
		origin_pairs = line.split('[')[2:]
		final_list = []
		for pair in origin_pairs:
			pair = pair.strip('],')
			pair = pair.strip(']]')
			elements = pair.split(',')
			elements[0] = elements[0].strip('"')
			if len(elements[1]) == 2:
				elements[1] = '00'+elements[1]
			elif len(elements[1]) == 3:
				elements[1] = '0'+elements[1]
			elif len(elements[1]) == 1:
				elements[1] = '000'+elements[1]
			if len(elements[2]) == 2:
				elements[2] = '00'+elements[2]
			elif len(elements[2]) == 3:
				elements[2] = '0'+elements[2]
			elif len(elements[2]) == 1:
				elements[2] = '000'+elements[2]
			final_list.append((elements[0],elements[1],elements[2]))
		flights[flight] = final_list
def pair_list(airport, flight):
	# Get pairs of airports that have direct flights or need connecting
	direct = []
	connect = []
	for Org in airport:
		for Des in airport:
			if Org != Des:
				if "{} to {}".format(Org, Des) in flight:
					direct.append((Org, Des))
				else:
					connect.append((Org, Des))
	return direct, connect
direct, connect = pair_list(airports, flights)
def transtime(time):
	# Transform string to minutes
	return 60 * int(time[:2]) + int(time[2:])
def judge(time1, time2):
	# Compare time
	time11 = time1
	time12 = time11 + 60*24
	time21 = time2
	time22 = time21 + 60*24
	diff1 = -(time11 - time21)
	diff2 = -(time12 - time21)
	diff3 = -(time11 - time22)
	diff4 = -(time12 - time22)
	diff = list(i for i in [diff1, diff2, diff3, diff4] if i > 0)
	if diff:
		return min(diff)
	else:
		return False

def route_suggest(Org, Des, connect_dict, time_max = 180, time_min = 120):
	''' 
	Select best route:
	Straight flight ranks by average delay time, 
	Connecting pair ranks by total time (including average arrival delay time for last flight)
	'''
	# Select Straight Flight
	label = '{} to {}'.format(Org, Des)
	if (Org, Des) in direct:
		suggest_flight = []
		for flight in flights[label]:
			flightlabel = label + ' ' + flight[0]
			if flightlabel in FlightDelay:
				delay = float(FlightDelay[flightlabel][0])
				suggest_flight.append((flight[0], delay, flight[1], flight[2]))
			else:
				pass
		sort_suggest = sorted(suggest_flight, key = lambda x: x[1])
		if sort_suggest:
			idx = min([len(sort_suggest),3])
			suggest = list('Flight Number: {}, depart at {}:{}, arrive at {}:{}'.format(i[0], i[2][:2], i[2][2:], i[3][:2], i[3][2:]) for i in sort_suggest[:idx])
			return 'straight flight', suggest
		else:
			return 'No flights available', None
	# Judge if there is potential connecting pair
	if not label in connect_dict:
		return 'No flights available', None
	# Select Connecting Pair
	potential = connect_dict[label]
	route_suggest = dict()
	# Judge every potential connecting pair, check whether the transition time meets our requirement after considering delay time
	for route in potential:
		potential_connect = []
		mid = route[1]
		label1 = '{} to {}'.format(Org, mid)
		potential_1 = flights[label1]
		label2 = '{} to {}'.format(mid, Des)
		potential_2 = flights[label2]
		for flight1 in potential_1:
			flightlabel1 = label1 + ' ' + flight1[0]
			if not flightlabel1 in FlightDelay:
				pass
			else:
				DepDelay, ArrDelay = FlightDelay[flightlabel1]
				Dep1 = transtime(flight1[1])
				Arr1 = transtime(flight1[2]) + float(ArrDelay)
				for flight2 in potential_2:
					flightlabel2 = label2 + ' ' + flight2[0]
					if not flightlabel2 in FlightDelay:
						pass
					else:
						DepDelay, ArrDelay = FlightDelay[flightlabel2]
						Dep2 = transtime(flight2[1]) + float(DepDelay)
						Arr2 = transtime(flight2[2]) + float(ArrDelay)
						transition_time = judge(Arr1, Dep2)
						if transition_time:
							if transition_time <= time_max and transition_time >= time_min:
								if Dep1 < Arr2:
									Total_time = Arr2 - Dep1
								else:
									Total_time = Arr2 - Dep1 + 60 * 24
								potential_connect.append((flight1[0],flight2[0], Total_time))
		if potential_connect:
			route_suggest[route] = potential_connect
	# Select the flight with minimal total time
	full_list = []
	for route in route_suggest:
		for pair in route_suggest[route]:
			full_list.append((route, pair[0], pair[1], pair[2]))
	sort_full_list = sorted(full_list, key = lambda x: x[3])
	if sort_full_list:
		idx2 = min([len(sort_full_list),3])
		suggest2 = list('{} to {} to {}: {} & {}'.format(i[0][0],i[0][1],i[0][2], i[1], i[2]) for i in sort_full_list[:idx2])
		return 'connecting flights', suggest2
	else:
		return 'No flights available', None
print(route_suggest('SJC', 'PHX', connect_dict))
