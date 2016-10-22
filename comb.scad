STRIP_COUNT = 8;
STRIP_WIDTH = 10;
STRIP_THICKNESS = 0.5;

LED_PITCH = 16.5;
LED_SIDE = 5;

COMPONENT_WIDTH = 4;
COMPONENT_LENGTH = 3;
COMPONENT_HEIGHT = 1;

TOOTH_LENGTH = LED_PITCH - STRIP_WIDTH;

COMB_WIDTH = LED_PITCH - LED_SIDE;
COMB_LENGTH = STRIP_COUNT * LED_PITCH + TOOTH_LENGTH;
COMB_HEIGHT = 2;

PIN_R = 2;
PIN_POS = 5;
PIN_DX = 2;
PIN_Y = 1.5;

CORD_HOLE_R = 2.5;
CORD_HOLE_POS = 5;
CORD_HOLE_Y = 7;

SYNCPAD_LENGTH = 11;

TOL = 0.1;

WIRE_HOLDER_LENGTH = 23;
WIRE_HOLDER_R = 3;
WIRE_D_1 = 2.9;
WIRE_D_2 = 2.3;
WIRE_D_3 = 1.2;

module wire_cutout(d, n=2) {
    union () {
        for (w=[0:(n-1)]) {
            translate ([w*d, COMB_WIDTH*2, -d/2]) {
                rotate ([90, 0, 0]) {
                    cylinder(100, d=d+TOL*2, $fn=20);
                }
            }
        }
        translate ([-d/3, -100, -d*0.8]) {
            cube ([d*(n-1/3), 200, 200]);
        }
    }
}

module for_every_strip () {
    for (i=[0:STRIP_COUNT-1]) {
        translate ([(i+.5) * LED_PITCH+TOOTH_LENGTH/2, 0, 0]) {
            children();
        }
    }
}

module comb (spin) translate ([0, 0, -COMB_HEIGHT]) {
    union () {
        translate ([-COMB_LENGTH/2, 0, 0]) {
            difference () {
                translate ([0, TOL, 0]) {
                    cube ([COMB_LENGTH, COMB_WIDTH-TOL, COMB_HEIGHT-STRIP_THICKNESS/2]);
                }
                if (spin>0) {
                    for_every_strip () {
                        translate ([-COMPONENT_WIDTH/2,
                                    -TOL,
                                    COMB_HEIGHT-COMPONENT_HEIGHT]) {
                            cube ([COMPONENT_WIDTH, COMPONENT_LENGTH, 100]);
                        }
                    }
                }
            }
            for (i=[0:STRIP_COUNT]) {
                translate ([i * LED_PITCH+TOL, 0, 0]) {
                    cube ([TOOTH_LENGTH-TOL*2, COMB_WIDTH, COMB_HEIGHT*2]);
                }
            }
            if (spin<0) {
                for_every_strip () {
                    translate ([-STRIP_WIDTH/2+TOL*2, -COMB_WIDTH, 0]) {
                        cube ([STRIP_WIDTH-TOL*4, COMB_WIDTH*2, COMB_HEIGHT-STRIP_THICKNESS/2]);
                    }
                }
            }
        }
        for (s=[-1,1]) scale ([s, 1, 1]) translate ([COMB_LENGTH/2, 0, 0]) {
            difference () {
                union () {
                    translate ([0, -COMB_WIDTH, 0]) {
                        cube ([SYNCPAD_LENGTH+s*TOL*2, COMB_WIDTH*2, COMB_HEIGHT]);
                    }
                    translate ([PIN_POS+PIN_DX*spin, PIN_Y, 0]) {
                        cylinder(COMB_HEIGHT*2+TOL*2, r=PIN_R-TOL, $fn=20);
                    }
                }
                translate ([PIN_POS-PIN_DX*spin, -PIN_Y, -1]) {
                    cylinder(COMB_HEIGHT*2+2, r=PIN_R+TOL, $fn=20);
                }
                for (y=[-1,1]) {
                    translate ([CORD_HOLE_POS, y*CORD_HOLE_Y, -1]) {
                        cylinder (COMB_HEIGHT+2, r=CORD_HOLE_R, $fn=20);
                    }
                }
            }
        }
        translate ([COMB_LENGTH/2+SYNCPAD_LENGTH, 0, 0]) {
            intersection () {
                hull () {
                    translate ([0, -COMB_WIDTH, 0]) {
                        cube ([1, COMB_WIDTH*2, 100]);
                    }
                    for (y=[-1,1]) translate ([WIRE_HOLDER_LENGTH-WIRE_HOLDER_R,
                                               y*(COMB_WIDTH-WIRE_HOLDER_R),
                                               0]) {
                        cylinder (100, r=WIRE_HOLDER_R, $fn=20);
                    }
                }
                difference () {
                    translate ([0, -COMB_WIDTH, 0]) {
                        cube ([100, COMB_WIDTH*2, COMB_HEIGHT*2]);
                    }
                    translate ([WIRE_D_1, 0, COMB_HEIGHT*2]) wire_cutout(WIRE_D_1);
                    translate ([WIRE_D_1*3.5, 0, COMB_HEIGHT*2]) wire_cutout(WIRE_D_2);
                    translate ([WIRE_D_1*5.25, 0, COMB_HEIGHT*2]) wire_cutout(WIRE_D_3, n=4);
                }
            }
        }
    }
}

comb(1);
% rotate ([180, 0, 0]) scale ([-1, 1, 1]) translate ([0, 0, -TOL]) comb(-1);

scale ([-1, 1, 1]) translate ([-WIRE_HOLDER_LENGTH, COMB_WIDTH*3, 0]) comb(-1);
