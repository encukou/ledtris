WIDTH = 40;

BRAIN_L = 73;
TOUCH_L = 93;

WALL_THICKNESS = 1;

TOP_H = 10;

BUTTON_R = 5;
BUTTON_H = 4;
BUTTON_DIST = 10;
BUTTON_ROUND_R = 1;
BUTTON_E = 0.5;

PBUTTON_SIDE = 6;
PBUTTON_LEG_POS = 5;
PBUTTON_LEG_R = 1;
PBUTTON_H = 5;

BUTTON_PAD_R = 7;
BUTTON_PAD_H = 1;

PAD_ROD_H = PBUTTON_H+BUTTON_PAD_H;
PAD_ROD_D = 3;

PAD_TOTAL_H = TOP_H - WALL_THICKNESS - PBUTTON_H;
PAD_BOTTOM_H = PAD_TOTAL_H - WALL_THICKNESS*2;

NODEMCU_L = 58;
NODEMCU_W = 31;
NODEMCU_ROUND_R = 3;

MCU_PIN_L = 37;
MCU_PIN_W = 31;
MCU_PIN_D = 1;
MCU_PIN_H = 9;
MCU_PIN_SEP = 2.5;

STRUT_R = 2;
STRUT_DEPTH = 1.5;

WIRE_D = 1;

TOL = 0.1;

SPRING_D = 4;
SPRING_COILED_L = 5;
SPRING_EXTENDED_L = 15;
SPRING_NUB_L = 2;
SPRING_NUB_D = 3;

BATTERY_L = 50;
BATTERY_D = 15;
BATTERY_PAD_NOOK = 2;
BATTERY_SHAFT_L = BATTERY_L*3+SPRING_COILED_L+WIRE_D;

SCREW_LOOSE_R = 1.9;
SCREW_SUPPORT_R = 3.5;
SCREW_TIGHT_R = 1.25;

BATTERY_DOOR_HANDLE_R = 1.5;
BATTERY_DOOR_HANDLE_H = 2;

module roundrect (h, w, l, r) {
    hull () {
        for (x=[-w/2+r, w/2-r]) for(y=[-l/2+r, l/2-r]) {
            translate ([x, y, 0]) {
                cylinder (h, r=r);
            }
        }
    }
}

module main_shape (h=10, R=10, dwall=0) {
    hull () {
        for (x=[-WIDTH/2, WIDTH/2]) for(y=[-BRAIN_L, TOUCH_L]) {
            translate ([x-R*sign(x), y-R*sign(y), 0]) {
                cylinder (h, r=R-dwall);
            }
        }
    }
}

module button_pad_pos () {
    translate ([0, 25, 0]) rotate ([0, 0, 90]) children();
    translate ([0, 55, 0]) children();
    translate ([0, 75, 0]) children();
}

module button_pos () {
    button_pad_pos () {
        for (x=[-BUTTON_DIST, BUTTON_DIST]) translate ([x, 0, 0]) {
            children();
        }
    }
}

module screw_pos () {
    translate ([0, TOUCH_L-SCREW_SUPPORT_R-WALL_THICKNESS, 0]) children ();
    translate ([-WIDTH/3, -BRAIN_L+SCREW_SUPPORT_R*2+WALL_THICKNESS, 0]) children ();
    translate ([WIDTH/3, -BRAIN_L+SCREW_SUPPORT_R*2+WALL_THICKNESS, 0]) children ();
}

module strut_pos () {
    children();
    translate ([10, 25, 0]) children();
    translate ([-10, 25, 0]) children();
    translate ([0, 45, 0]) children();
    translate ([0, 65, 0]) children();
    translate ([0, -67, 0]) children();
}

module button_pad () {
    difference () {
        hull () {
            for (x=[-10, 10]) translate ([x, 0, 0]) {
                cylinder (BUTTON_PAD_H, r=BUTTON_PAD_R);
            }
        }
        translate ([0, 0, -1]) cylinder (100, d=PAD_ROD_D+TOL, $fn=10);
    }
    for (x=[-BUTTON_DIST, BUTTON_DIST]) translate ([x, 0, 0]) {
        hull () {
            rotate_extrude(convexity = 10) {
                for (y=[BUTTON_H-BUTTON_ROUND_R, BUTTON_ROUND_R]) {
                    translate ([BUTTON_R-BUTTON_ROUND_R, y, 0]) {
                        circle (BUTTON_ROUND_R, $fn=20);
                    }
                }
            }
        }
    }
}

module top_cover () {
    difference () {
        union () {
            difference () {
                main_shape (h=TOP_H);
                translate ([0, 0, WALL_THICKNESS]) {
                    main_shape (h=TOP_H, dwall=WALL_THICKNESS);
                }
            }
            strut_pos () cylinder (TOP_H+STRUT_DEPTH, r=STRUT_R-TOL, $fn=20);
            difference () {
                screw_pos () cylinder (TOP_H, r=SCREW_SUPPORT_R, $fn=20);
                translate ([-100, 0, TOP_H-PAD_TOTAL_H]) cube ([200, 200, 200]);
            }
            translate ([0, -BRAIN_L+WALL_THICKNESS*2, WALL_THICKNESS]) {
                for (x=[-1,1]) translate ([x*BATTERY_D/4-WALL_THICKNESS/2, 0, 0]) {
                    s = 2;
                    h = -5;
                    hull () rotate ([0, 90, 0]) {
                        cylinder (WALL_THICKNESS, d=WALL_THICKNESS);
                        translate ([0, s, 0]) cylinder (WALL_THICKNESS, d=WALL_THICKNESS);
                        translate ([h, s, 0]) cylinder (WALL_THICKNESS, d=WALL_THICKNESS);
                    }
                }
            }
        }
        translate ([0, 0, -1]) {
            button_pos () cylinder (100, r=BUTTON_R+BUTTON_E);
            screw_pos () cylinder (100, r=SCREW_LOOSE_R, $fn=10);
        }
        translate ([0, -BRAIN_L+WALL_THICKNESS-TOL, TOP_H-TOL*2]) {
            rotate ([90, 0, 0]) {
                cylinder (100, r=BATTERY_DOOR_HANDLE_R+TOL, $fn=20);
            }
            w = BATTERY_D+BATTERY_PAD_NOOK+TOL*2;
            translate ([-w/2, 0, -100]) {
                cube ([w, WALL_THICKNESS+TOL*2, 200]);
            }
        }
    }
}

module bottom_cover () {
    difference () {
        intersection () {
            main_shape (h=100);
            translate ([0, 100, 0]) rotate ([90, 0, 0]) {
                cylinder(200, d=WIDTH);
            }
        }
        union () translate ([0, -BRAIN_L+WALL_THICKNESS*2, 0]) {
            {
                // Main battery shaft
                translate ([-BATTERY_D/2, -100, BATTERY_D/2+WALL_THICKNESS*2]) {
                    cube ([BATTERY_D, BATTERY_SHAFT_L+100, BATTERY_D/2]);
                }
                translate ([0, -100, BATTERY_D/2+WALL_THICKNESS*2]) {
                    rotate ([-90, 0, 0]) cylinder (BATTERY_SHAFT_L+100, d=BATTERY_D, $fn=80);
                }
            }
            translate ([0, BATTERY_SHAFT_L, 0]) {
                // Spring terminal
                translate ([-BATTERY_D/2-BATTERY_PAD_NOOK, -TOL, -1]) {
                    cube ([BATTERY_D+BATTERY_PAD_NOOK*2,
                           WIRE_D+TOL*2, BATTERY_D+WALL_THICKNESS*2+1]);
                }
                spring_hole_d = SPRING_D+WALL_THICKNESS;
                translate ([-spring_hole_d/2, -SPRING_EXTENDED_L, -1]) {
                    cube ([spring_hole_d, SPRING_EXTENDED_L, spring_hole_d]);
                }
            }
            translate ([0, 0, 0]) {
                // Door terminal
                translate ([-BATTERY_PAD_NOOK-BATTERY_D/2, -WALL_THICKNESS, -1]) {
                    cube ([BATTERY_D+BATTERY_PAD_NOOK*2, WALL_THICKNESS+TOL, BATTERY_D+WALL_THICKNESS*2+1]);
                }
                rotate ([90, 0, 0]) hull () for (z=[0, BATTERY_D/2]) {
                    translate ([0, z, -WIRE_D]) {
                        cylinder (BATTERY_DOOR_HANDLE_H+WALL_THICKNESS+100,
                                r=BATTERY_DOOR_HANDLE_R+TOL,
                                $fn=24);
                    }
                }
            }
            translate ([0, -BRAIN_L/2+NODEMCU_L, -1]) {
                // Brain pins
                hole_w = MCU_PIN_SEP + MCU_PIN_D + TOL;
                for (x=[-1, 1]) translate ([x*(MCU_PIN_W/2)-hole_w/2, 0, 0]) {
                    cube ([hole_w, MCU_PIN_L, MCU_PIN_H+TOL+1]);
                }
            }
        }
        screw_pos () {
            // Screw holes
            cylinder (WIDTH/4, r=SCREW_TIGHT_R, $fn=10);
        }
        translate ([0, 0, -1]) strut_pos () {
            cylinder (STRUT_DEPTH+1, r=STRUT_R+TOL, $fn=20);
        }
    }
}

module battery_end_spring () {
    w = BATTERY_D + BATTERY_PAD_NOOK*2 - TOL*2;
    translate ([-w/2, -BATTERY_D/2, 0]) {
        cube ([w, BATTERY_D+WALL_THICKNESS*2-TOL, WALL_THICKNESS-TOL]);
    }
    cylinder (WALL_THICKNESS+SPRING_NUB_L, d=SPRING_NUB_D, $fn=10);
    %cylinder (WALL_THICKNESS, d=BATTERY_D); 
}

module battery_end_door () {
    difference () {
        union () {
            w = BATTERY_D + BATTERY_PAD_NOOK*2 - TOL*2;
            translate ([-w/2, -BATTERY_D/2, 0]) {
                cube ([w, BATTERY_D, WALL_THICKNESS-TOL]);
            }
            r = BATTERY_DOOR_HANDLE_R;
            translate ([0, -BATTERY_D/2+r, 0]) {
                cylinder (BATTERY_DOOR_HANDLE_H+WALL_THICKNESS,
                        r=BATTERY_DOOR_HANDLE_R,
                        $fn=24);
            }
            %cylinder (WALL_THICKNESS, d=BATTERY_D); 
        }
        for (r=[0, 180]) rotate ([0, 0, r]) {
            translate ([-WIRE_D/4, SPRING_NUB_D/2, -1]) {
                cube ([WIRE_D/2, BATTERY_D/4, WIRE_D/2+1]);
            }
        }
    }
}

module _add_screw_supports () {
    difference () {
        union () {
            children ();
        }
    }
}

module button_support () {
    difference () {
        union () {
            intersection () {
                translate ([0, 0, -PAD_BOTTOM_H]) {
                    main_shape (h=WALL_THICKNESS*2+PAD_BOTTOM_H, dwall=WALL_THICKNESS+TOL);
                }
                translate ([-100, 0, -PAD_BOTTOM_H]) cube([200, 100, 100]);
            }
            button_pad_pos () {
                translate ([-PAD_ROD_D/2, -PAD_ROD_D, WALL_THICKNESS]) {
                    cube ([PAD_ROD_D, PAD_ROD_D*2, PBUTTON_H-TOL*2]);
                }
                cylinder (WALL_THICKNESS+PAD_ROD_H, d=PAD_ROD_D-TOL*2, $fn=10);
            }
        }
        difference () {
            translate ([0, 0, -PAD_BOTTOM_H-1]) {
                main_shape (h=PAD_BOTTOM_H+1, dwall=WALL_THICKNESS*3);
            }
            screw_pos () translate ([0, 0, -PAD_BOTTOM_H]) {
                cylinder (PAD_TOTAL_H, r=SCREW_SUPPORT_R, $fn=20);
            }
        }
        button_pos () {
            rotate ([0, 0, 45]) {
                translate ([-(PBUTTON_SIDE-TOL)/2, -(PBUTTON_SIDE-TOL)/2, WALL_THICKNESS]) {
                    cube ([PBUTTON_SIDE+TOL, PBUTTON_SIDE+TOL, 100]);
                }
                for (x=[PBUTTON_SIDE/2, -PBUTTON_SIDE/2]) {
                    for (y=[PBUTTON_LEG_POS/2, -PBUTTON_LEG_POS/2]) {
                        translate ([x, y, -1]) cylinder (100, r=PBUTTON_LEG_R, $fn=10);
                    }
                }
            }
        }
        strut_pos () translate ([0, 0, -1]) {
            cylinder (100, r=STRUT_R+TOL, $fn=20);
        }
        screw_pos () translate ([0, 0, -100]) {
            cylinder (200, r=SCREW_LOOSE_R, $fn=10);
        }
    }
    button_pos () {
        scale ([1, 1, -1]) cylinder (PAD_BOTTOM_H, d=PBUTTON_SIDE/2, $fn=20);
    }
}

module button_support_1 () {
    intersection () {
        translate ([0, 0, -WALL_THICKNESS-TOL/2]) button_support ();
        translate ([-100, -100, 0]) cube([200, 200, 100]);
    }
}

module button_support_2 () {
    rotate ([0, 180, 0]) intersection () {
        translate ([0, 0, -WALL_THICKNESS]) button_support ();
        translate ([-100, -100, -100]) cube([200, 200, 100]);
    }
}

union () {
    top_cover ();
    translate ([45, 0, 0]) bottom_cover ();
    translate ([85, 15, 0]) button_pad_pos () button_pad ();
    translate ([85, -70, 0]) button_support_1 ();
    translate ([125, -70, 0]) button_support_2();
    translate ([110, 35, 0]) battery_end_spring ();
    translate ([130, 35, 0]) battery_end_door ();
}

%translate ([-70, 0, 0]) {
    translate ([0, 0, TOP_H]) rotate ([0, 180, 0]) top_cover ();
    rotate ([0, 180, 0]) bottom_cover ();
    #button_pad_pos () translate ([0, 0, TOP_H-WALL_THICKNESS*2]) button_pad ();

    translate ([-50, 0, 0]) rotate ([0, 180, 0]) bottom_cover ();

    translate ([-140, 0, 0]) button_support ();
}
%translate ([85, 15, -TOL]) strut_pos () cylinder (TOL, r=STRUT_R);
%translate ([0, 0, 2]) rotate ([0, 180, 0]) button_pad_pos () button_pad ();

% translate ([-165, 0, 0]) intersection () {
    bottom_cover ();
    translate ([-100, -100, 0]) cube ([200, 200, BATTERY_D]);
}

/*
union () {
    main_shape ();
    difference () {
        intersection () {
            translate ([0, 0, -WIDTH]) main_shape(H=WIDTH);
            rotate ([90, 0, 0]) translate ([0, 0, -100]) {
                scale ([1, 0.9, 1]) cylinder (200, d=WIDTH);
            }
        }
        translate ([0, 100, -10]) rotate ([90, 0, 0]) cylinder (200, d=13);
    }
}
*/
