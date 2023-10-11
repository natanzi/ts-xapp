from ricxappframe.xapp_frame import Alarm, AlarmManager

# Initialize the AlarmManager
alarm_manager = AlarmManager()

# Define alarms
handover_failure_alarm = Alarm(
    alarm_id="1001",
    alarm_text="Handover Failure",
    cause="Handover attempted but failed",
    severity="MAJOR",
    proposed_repair_action="Check connectivity with target cell or adjust handover parameters",
    additional_info={}
)

data_retrieval_failure_alarm = Alarm(
    alarm_id="1002",
    alarm_text="Data Retrieval Failure",
    cause="Failed to retrieve data from E2 node",
    severity="MINOR",
    proposed_repair_action="Check E2 node status and connectivity",
    additional_info={}
)

cell_congestion_alarm = Alarm(
    alarm_id="1003",
    alarm_text="Cell Congestion",
    cause="High traffic causing cell congestion",
    severity="MAJOR",
    proposed_repair_action="Consider load balancing or expanding capacity",
    additional_info={}
)

# Function to raise an alarm
def raise_alarm(alarm):
    alarm_manager.raise_alarm(alarm)

# Handlers for specific scenarios
def handle_handover_failure(event_details):
    handover_failure_alarm.additional_info = event_details
    raise_alarm(handover_failure_alarm)

def handle_data_retrieval_failure(event_details):
    data_retrieval_failure_alarm.additional_info = event_details
    raise_alarm(data_retrieval_failure_alarm)

def handle_cell_congestion(event_details):
    cell_congestion_alarm.additional_info = event_details
    raise_alarm(cell_congestion_alarm)
