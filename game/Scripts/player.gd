extends Node2D
class_name Player

var player_name: String
var role: String
var id: int
var current_action: String

func _ready() -> void:
	for child in get_children():
		if child is HostPlayer:
			self.name = "HostPlayer"
