from autograder.models import GirderGeometry


def determine_flange_width(fl_h, rib_h, rib_b, rib_l0, s_tr, s_long, rib_type):
    """ Determines effective width of flange for T-sections
    fl_h - flange thickness,
    rib_h - height of a rib,
    rib_b - width of the rib wall,
    rib_l0 - effective span of the rib,
    s_tr - distance between transverse ribs (perpendicular to currently considering),
    s_long - distance between longitudinal ribs,
    rib_type - 'cons' for rib with cantilevers on the flange ('T-section'),
                'noCons' - for rib with no cantilevers """

    if rib_type == "cons":
        rib_h = rib_h / 100
    rib_b = rib_b / 100
    fl_w_less = list()

    # print("flange_w", fl_h, rib_h, rib_b, rib_l0, s_tr, s_long)

    main_cond_w = (1 / 3) * rib_l0 + rib_b
    fl_w_less.append(main_cond_w)

    if fl_h >= 0.1 * rib_h:
        a_cond_w = s_long + rib_b
        fl_w_less.append(a_cond_w)
    elif s_tr > s_long and fl_h < 0.1 * rib_h:
        b_cond_w = 12 * fl_h + rib_b
        fl_w_less.append(b_cond_w)

    if rib_type == 'cons':  # we have flange with consoles
        if fl_h >= 0.1 * rib_h:
            c_cond_w_1 = 12 * fl_h + rib_b
            fl_w_less.append(c_cond_w_1)
        elif 0.05 * rib_h <= fl_h < 0.1 * rib_h:  # elif 0.05 * rib_h <= fl_h and fl_h < 0.1 * rib_h :
            c_cond_w_2 = 6 * fl_h + rib_b
            fl_w_less.append(c_cond_w_2)
        elif fl_h < 0.05 * rib_h:
            c_cond_w_3 = rib_b
            fl_w_less.append(c_cond_w_3)

    fl_w = min(fl_w_less)

    return fl_w
