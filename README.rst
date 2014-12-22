A tetromino-stacking game for the Micropython Pyboard and
eight 144-LED WS2812 strips.


See the `youtube video`_ for a demo.

.. _youtube video: https://www.youtube.com/watch?v=BopiYBx1JOs

Software
--------

Copy ``strips.py`` and ``main.py`` to your pyboard.

If you have more or fewer than 144 LEDs in one strip, adjust ``SIZE``
at the top of ``main.py``.

.. _micropython-ws2812: https://github.com/JanBednarik/micropython-ws2812


Hardware
--------

Note that the LED driver depends on Pyboard's CPU (both instruction set and
frequency); it might not work on other Micropython boards.

I recommend using separate dedicated power sources for the LEDs, to ensure
there's enough juice left for the controller. Be sure to use a common ground
between LEDs and the Pyboard.


Connect (+) and (-) of *all* LED strips to a 5V power source.
Connect (-) of LED strips to GND on the Pyboard.
Connect X1-X8 on the Pyboard to DATA pins of the eight strips.

Connect four buttons buttons between VIN and these pins on the Pyboard:

=== ============
Pin Function
=== ============
Y1  Left
Y2  Rotate
Y3  Right
Y4  Fast falling
=== ============

(Left/Right might be reversed depending on how you lay out the LED strips)


Operation
---------

Play using the four buttons!
An exception is raised should you lose.
