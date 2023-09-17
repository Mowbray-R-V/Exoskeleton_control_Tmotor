import canlib.canlib as clb


def setUpChannel(channel: int = 0, openFlags=clb.Open.ACCEPT_VIRTUAL, outputControl=clb.Driver.NORMAL):
    """Function which initializes the CAN protocol

    Args:
        channel (int): Channel number. Defaults to 0.
        openFlage (int): Accepts all input flags
        outputControl (int): clb Output Control Drivers

    Returns:
        Channel Object: Initialized channel
    """

    ch = clb.openChannel(channel, openFlags)
    ch.setBusOutputControl(outputControl)
    ch.busOn()
    return ch


def tearDownChannel(ch):
    """Closes the CAN channel

    Args:
        ch: Channel Object
    """

    ch.busOff()
    ch.close()


def start_channel(channel_number: int):
    """Sets up channel

    Args:
        channel_number (int): Desired channel number

    Returns:
        Channel Object: Channel object with the desired channel number
    """

    ch = setUpChannel(channel=channel_number)
    return ch
