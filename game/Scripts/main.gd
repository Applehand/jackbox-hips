extends Node

const API_BASE_URL = "http://127.0.0.1:8000/"
var current_session_id = null
var access_code = ""

var current_game = null
var players: Array[Player] = []

@onready var create_lobby_button: Button = $Control/Control/HBoxContainer/CreateLobbyButton
@onready var end_lobby_button: Button = $Control/Control/HBoxContainer/EndLobbyButton
@onready var access_code_label: Label = $Control/Control2/Label

var packed_player_scene: PackedScene = preload("res://Scenes/player.tscn")


func _ready() -> void:
	create_lobby_button.connect("pressed", create_lobby_req)
	end_lobby_button.connect("pressed", end_lobby_req)


func create_lobby_req():
	if current_session_id:
		print("Session already created.")
		return
	var url = API_BASE_URL + "sessions"
	var req = HTTPRequest.new()
	add_child(req)
	req.request_completed.connect(_on_session_created)
	
	var body = JSON.stringify({"host_name": "Jake"})
	var error = req.request(url, [], HTTPClient.METHOD_POST, body)
	if error != OK:
		push_error("An error occurred with the POST request.")


func end_lobby_req():
	if not current_session_id:
		print("No session exists.")
		return
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
	print("Session created response: ", response)
	
	access_code = response.access_code
	current_session_id = response.session_id
	
	access_code_label.text = access_code
	
	var host_player: Player = packed_player_scene.instantiate()
	add_child(host_player)
	players.append(host_player)
	
	host_player.player_name = response.host_player.name
	host_player.role = response.host_player.role
	host_player.id = response.host_player.id
	host_player.current_action = response.host_player.current_action
	

func _on_session_deleted(result, response_code, headers, body):
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	print(response.message)
	
	for player in players:
		players.erase(player)
		player.queue_free()
	
	access_code_label.text = ""
	current_session_id = null
