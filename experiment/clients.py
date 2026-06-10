from dataclasses import dataclass

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


@dataclass
class RobotClients:
    audio_client: AudioClient
    loco_client: LocoClient


def initialize_robot_clients(network_interface: str) -> RobotClients:
    """Initialize the Unitree SDK channel and return ready-to-use robot clients."""
    ChannelFactoryInitialize(0, network_interface)

    audio_client = AudioClient()
    audio_client.SetTimeout(10.0)
    audio_client.Init()
    print("Audio client initialized")

    loco_client = LocoClient()
    loco_client.SetTimeout(10.0)
    loco_client.Init()
    print("Loco client initialized")

    return RobotClients(audio_client=audio_client, loco_client=loco_client)