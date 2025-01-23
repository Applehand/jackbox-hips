extends Node

const API_BASE_URL = "http://127.0.0.1:8000/"
var lobby_req = null
var current_session_id = null
var access_code = ""

var current_game = null
var players: Array[Player] = []

@onready var create_lobby_button: Button = $Control/Control/HBoxContainer/CreateLobbyButton
@onready var end_lobby_button: Button = $Control/Control/HBoxContainer/EndLobbyButton
@onready var access_code_label: Label = $Control/Control/HBoxContainer/AccessCodeLabel
@onready var name_field: LineEdit = $Control/Control/HBoxContainer/NameField
@onready var password_field: LineEdit = $Control/Control/HBoxContainer/PasswordField

var packed_player_scene: PackedScene = preload("res://Scenes/player.tscn")


func _ready() -> void:
	create_lobby_button.connect("pressed", create_lobby_req)
	end_lobby_button.connect("pressed", end_lobby_req)


func create_lobby_req():
	if current_session_id:
		print("Session already created.")
		return
	if not name_field.text or not password_field.text:
		print("Please enter a character name and host password.")
		return
	var url = API_BASE_URL + "sessions"
	lobby_req = HTTPRequest.new()
	add_child(lobby_req)
	lobby_req.request_completed.connect(_on_session_created)
	
	var body = JSON.stringify(
		{"host_name": name_field.text,
		 "host_password": password_field.text}
		)
		
	var error = lobby_req.request(url, [], HTTPClient.METHOD_POST, body)
	if error != OK:
		push_error("An error occurred with the POST request.")


func end_lobby_req():
	if not current_session_id:
		print("No session exists.")
		return
	var url = API_BASE_URL + "sessions/" + str(current_session_id)
	lobby_req = HTTPRequest.new()
	add_child(lobby_req)
	lobby_req.request_completed.connect(_on_session_deleted)

	var error = lobby_req.request(url, [], HTTPClient.METHOD_DELETE)
	if error != OK:
		push_error("An error occurred with the DELETE request.")


func _on_session_created(result, response_code, headers, body):
	lobby_req.queue_free()
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	print("Session created response: ", response)
	
	access_code = response.access_code
	current_session_id = response.session_id
	
	access_code_label.text = access_code
	
	var host_player: Player = packed_player_scene.instantiate()
	var host_role = HostPlayer.new()
	host_player.add_child(host_role)
	
	add_child(host_player)
	players.append(host_player)
	
	host_player.player_name = response.host_player.name
	host_player.role = response.host_player.role
	host_player.id = response.host_player.id
	host_player.current_action = response.host_player.current_action
	

func _on_session_deleted(result, response_code, headers, body):
	lobby_req.queue_free()
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	print(response.message)
	
	for player in players:
		players.erase(player)
		player.queue_free()
	
	access_code_label.text = ""
	current_session_id = null
