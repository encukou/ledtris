STRIP_COUNT = 8;
STRIP_WIDTH = 10;
STRIP_THICKNESS = 0.5;

LED_PITCH = 16.5;
LED_SIDE = 8;

COMPONENT_WIDTH = 4;
COMPONENT_LENGTH = 3;
COMPONENT_HEIGHT = 1;

TOOTH_LENGTH = LED_PITCH - STRIP_WIDTH;

COMB_WIDTH = LED_PITCH - LED_SIDE;
COMB_LENGTH = STRIP_COUNT * LED_PITCH + TOOTH_LENGTH;
COMB_HEIGHT = 2;

PIN_R = 2;
PIN_POS = [3];

CORD_HOLE_R = 2.5;
CORD_HOLE_POS = [10];
CORD_HOLE_Y = 3.5;

SYNCPAD_LENGTH = 14;

TOL = 0.1;

WIRE_HOLDER_LENGTH = 19;
WIRE_HOLDER_R = 2;
WIRE_D_1 = 2.5;
WIRE_D_2 = 2;
WIRE_D_3 = 1;

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

module comb () translate ([0, 0, -COMB_HEIGHT]) {
    union () {
        translate ([-COMB_LENGTH/2, 0, 0]) {
            difference () {
                cube ([COMB_LENGTH, COMB_WIDTH, COMB_HEIGHT-STRIP_THICKNESS/2]);
                for (i=[0:STRIP_COUNT]) {
                    translate ([(i+.5) * LED_PITCH+TOOTH_LENGTH/2-COMPONENT_WIDTH/2,
                                -TOL,
                                COMB_HEIGHT-COMPONENT_HEIGHT]) {
                        cube ([COMPONENT_WIDTH, COMPONENT_LENGTH, 100]);
                    }
                }
            }
            for (i=[0:STRIP_COUNT]) {
                translate ([i * LED_PITCH+TOL, 0, 0]) {
                    cube ([TOOTH_LENGTH-TOL*2, COMB_WIDTH, COMB_HEIGHT*2]);
                }
            }
        }
        for (s=[-1,1]) scale ([s, 1, 1]) translate ([COMB_LENGTH/2, 0, 0]) {
            difference () {
                union () {
                    translate ([0, -COMB_WIDTH, 0]) {
                        cube ([SYNCPAD_LENGTH+s*TOL*2, COMB_WIDTH*2, COMB_HEIGHT]);
                    }
                    for (x=PIN_POS) translate ([x, COMB_WIDTH/2, 0]) {
                        cylinder(COMB_HEIGHT*2+TOL*2, r=PIN_R-TOL, $fn=20);
                    }
                }
                for (x=PIN_POS) translate ([x, -COMB_WIDTH/2, -1]) {
                    cylinder(COMB_HEIGHT*2+2, r=PIN_R+TOL, $fn=20);
                }
                for (x=CORD_HOLE_POS) for (y=[-1,1]) {
                    translate ([x, y*CORD_HOLE_Y, -1]) {
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

comb();
% rotate ([180, 0, 0]) scale ([-1, 1, 1]) translate ([0, 0, -TOL]) comb();

scale ([-1, 1, 1]) translate ([-WIRE_HOLDER_LENGTH, COMB_WIDTH*3, 0]) comb();
