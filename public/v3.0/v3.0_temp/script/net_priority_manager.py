import subprocess
import time

# Define the list of network interfaces to test
interfaces = ["eth0", "wlan0", "wwan0"]
# Define the test server to ping
test_server = "8.8.8.8"

ping_result = {}
last_ping_result = {}

# Function to run ping and get metrics
def get_ping_metrics(interface):
    try:
        ping_result = subprocess.check_output(
            ["ping", "-I", interface, "-c", "4", "-q", test_server],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # Extract RTT and packet loss from the ping result
        rtt_line = [line for line in ping_result.split("\n") if "rtt min/avg/max/mdev" in line][0]
        packet_loss_line = [line for line in ping_result.split("\n") if "packet loss" in line][0]

        rtt = float(rtt_line.split("/")[4])
        packet_loss = float(packet_loss_line.split(",")[2].split("%")[0])

        return rtt, packet_loss
    except subprocess.CalledProcessError as e:
        # Handle errors, e.g., if ping fa3.ils
        return None, None


last_roll = None
def switch_metric(roll):
    global last_roll
    metric_val = []
    if roll == 0:  #priority eth0
        metric_val = [200,400,600]
    if roll == 1: #priority wlan0
        metric_val = [600,200,400]
    if roll == 2: #priority wwan0
        metric_val = [400,600,200]

    if last_roll != roll:
        try:
            print("network priority changes!")
            subprocess.run(["ifmetric", 'eth0', str(metric_val[0])], check=True)
            time.sleep(5)
            subprocess.run(["ifmetric", 'wlan0', str(metric_val[1])], check=True)
            time.sleep(5)
            subprocess.run(["ifmetric", 'wwan0', str(metric_val[2])], check=True)
            time.sleep(5)
            last_roll = roll
        except:
            pass


def metric_rule():
    if ping_result['eth0']: #priority eth0
        switch_metric(0)
        print("priority eth0")
    else:
        if ping_result['wlan0']: #priority wlan0
            switch_metric(1)
            print("priority wlan0")
        else:
            if ping_result['wwan0']: #priority wwan0
                switch_metric(2)
                print("priority wwan0")
            else:
                print("not connected to internet")

for interface in interfaces:
    ping_result[interface] = False


while 1:
    time.sleep(10)
    for interface in interfaces:
        rtt, packet_loss = get_ping_metrics(interface)
        if rtt is not None and packet_loss is not None:
            ping_result[interface] = True
        if rtt == None or packet_loss == None:
            ping_result[interface] = False

    print(ping_result)
    try:
        metric_rule()
    except:
        print("something went wrong")