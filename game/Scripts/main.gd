extends Node

const API_BASE_URL = "http://127.0.0.1:8000/"
var current_session_id
var access_code = ""

@onready var create_lobby_button: Button = $Control/Control/HBoxContainer/CreateLobbyButton
@onready var end_lobby_button: Button = $Control/Control/HBoxContainer/EndLobbyButton
@onready var access_code_label: Label = $Control/Control2/Label


func _ready() -> void:
	create_lobby_button.connect("pressed", create_lobby_req)
	end_lobby_button.connect("pressed", end_lobby_req)


func create_lobby_req():
	var url = API_BASE_URL + "sessions"
	var req = HTTPRequest.new()
	add_child(req)
	req.request_completed.connect(_on_session_created)
	
	var body = JSON.stringify({"host_name": "Jake"})
	var error = req.request(url, [], HTTPClient.METHOD_POST, body)
	if error != OK:
		push_error("An error occurred with the POST request.")


func end_lobby_req():
	var url = API_BASE_URL + "sessions/" + str(current_session_id)
	var req = HTTPRequest.new()
	add_child(req)
	req.request_completed.connect(_on_session_deleted)

	var error = req.request(url, [], HTTPClient.METHOD_DELETE)
	if error != OK:
		push_error("An error occurred with the DELETE request.")


func _on_session_created(result, response_code, headers, body):
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	
	access_code = response.access_code
	current_session_id = response.session_id
	
	access_code_label.text = access_code


func _on_session_deleted(result, response_code, headers, body):
	access_code_label.text = ""
	current_session_id = null
	print("Current session ended.")
