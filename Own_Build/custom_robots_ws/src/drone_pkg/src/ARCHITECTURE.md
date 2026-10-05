# Controller Architecture

```text
/cmd_vel ──> manual_drone_controller ──> Gazebo /set_entity_state service ──> drone pose
```

This controller bypasses flight dynamics: it is a simple visual/manual motion demonstration. It must use the same entity name that the Gazebo launch passes to the spawner.
