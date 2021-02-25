import csv
import matplotlib.pyplot as plt
import statistics


def read_csv(filename, start_row, column):
    data = []

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar=',')
        for n, row in enumerate(reader):
            if n < start_row:
                continue

            data.append(float(row[column]))

    return data


def delete_overflows(time, data):
    list_length = len(data)
    for i in range(0, list_length):
        index_mirrored = list_length - i - 1
        if data[index_mirrored] == 0:
            del (data[index_mirrored])
            del (time[index_mirrored])

    return [time, data]


def fit_data_to_time_list(time, data):
    interval = 60
    absolute_max_time = int(time[len(time) - 1])

    result = []
    time_list = []
    for t in range(int(interval / 2), absolute_max_time - int(interval / 2), 120):
        time_list.append(t)

    x_pos_min = 0
    x_pos_max = 0
    for time_now in time_list:
        t_min = time_now - interval / 2
        t_max = time_now + interval / 2

        # find x_point index for t_min
        while t_min > time[x_pos_min]:
            x_pos_min += 1

        # find x_point index for t_max
        while t_max > time[x_pos_max]:
            x_pos_max += 1

        # get data sublist based on interval
        data_sublist = []
        for position in range(x_pos_min, x_pos_max + 1):
            data_sublist.append(data[position])

        # get mean value of data sublist and append to result list
        result.append(round(statistics.median(data_sublist), 2))

        print(time_now)

    return [time_list, result]


def format_time(time_list):
    # format time data
    start_time = time_list[0]
    for n in range(0, len(time_list)):
        time_list[n] = round(time_list[n] - start_time, 2) / 1000

    return time_list


def pdc_shift(time, data):
    indexes = [0, 0]
    times = [60, 3660]
    step = 0
    for i in range(0, 2):
        while times[step] > time[indexes[step]]:
            indexes[step] += 1
        step += 1

    time_pol = time[indexes[0]:indexes[1] - 1]
    data_pol = data[indexes[0]:indexes[1] - 1]

    time_depol = time[indexes[1] + 1 - 1:len(time) - 1]
    data_depol = data[indexes[1] + 1 - 1:len(data) - 1]

    # shift pol list by t1 (init time, normally 60 seconds)
    time_pol = [round(element - times[0], 2) for element in time_pol]

    # shift depol time list
    time_depol = [round(element - times[1], 2) for element in time_depol]

    return [time_pol, data_pol, time_depol, data_depol]


def pdc_curve(time_pol, data_pol, time_depol, data_depol):
    if len(data_pol) > len(data_depol):
        length = len(data_depol)
        pdc_time = time_depol
    else:
        length = len(data_pol)
        pdc_time = time_pol

    pdc_data = []
    for i in range(length):
        pdc_data.append(round(data_pol[i] + data_depol[i], 2))

    return [pdc_time, pdc_data]


def material_plot_e_field_5():
    file_silicon = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_silicon_electrometer_1kV.txt"
    file_epoxy = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_epoxy_1mm_electrometer_500V.txt"

    # get data and delete overflows
    [time_silicon, data_silicon] = delete_overflows(read_csv(file_silicon, 12, 2), read_csv(file_silicon, 12, 4))
    [time_epoxy, data_epoxy] = delete_overflows(read_csv(file_epoxy, 12, 2), read_csv(file_epoxy, 12, 4))

    # format time (absolute time to seconds starting from zero)
    time_silicon = format_time(time_silicon)
    time_epoxy = format_time(time_epoxy)

    # make pdc shift
    [time_pol_silicon, data_pol_silicon, time_depol_silicon, data_depol_silicon] = pdc_shift(time_silicon, data_silicon)
    [time_pol_epoxy, data_pol_epoxy, time_depol_epoxy, data_depol_epoxy] = pdc_shift(time_epoxy, data_epoxy)

    # fit pdc shift data to constant time intervals
    [time_pol_silicon_fit, data_pol_silicon_fit] = fit_data_to_time_list(time_pol_silicon, data_pol_silicon)
    [time_depol_silicon_fit, data_depol_silicon_fit] = fit_data_to_time_list(time_depol_silicon, data_depol_silicon)
    [time_pol_epoxy_fit, data_pol_epoxy_fit] = fit_data_to_time_list(time_pol_epoxy, data_pol_epoxy)
    [time_depol_epoxy_fit, data_depol_epoxy_fit] = fit_data_to_time_list(time_depol_epoxy, data_depol_epoxy)

    # pdc shift
    [time_pdc_silicon, data_pdc_silicon] = pdc_curve(time_pol_silicon_fit, data_pol_silicon_fit, time_depol_silicon_fit,
                                                     data_depol_silicon_fit)
    [time_pdc_epoxy, data_pdc_epoxy] = pdc_curve(time_pol_epoxy_fit, data_pol_epoxy_fit, time_depol_epoxy_fit,
                                                 data_depol_epoxy_fit)

    # create plot for SiR
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-40, 40])
    plt.plot(time_pol_silicon, data_pol_silicon, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_silicon, data_depol_silicon, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_silicon_fit, data_pol_silicon_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_silicon_fit, data_depol_silicon_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_silicon, data_pdc_silicon, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for SiR (E = 5 kV/cm)")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_SiR_5kVpercm.png", dpi=300)
    plt.show()

    # create plot for epoxy
    plt.cla()
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-3, 3])
    plt.plot(time_pol_epoxy, data_pol_epoxy, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_epoxy, data_depol_epoxy, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_epoxy_fit, data_pol_epoxy_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_epoxy_fit, data_depol_epoxy_fit, "darkorange", mfc='None', markevery=5, marker='d',
             label="Depolarization current fitted data")
    plt.plot(time_pdc_epoxy, data_pdc_epoxy, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for Epoxy (E = 5 kV/cm)")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_epoxy_5kVpercm.png", dpi=300)
    plt.show()


def material_plot_e_field_50():
    file_pet = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_pet_electrometer_115V_Num_1.txt"
    file_pe = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_pe_electrometer_600V_Num_1.txt"
    file_pvc = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_pvc_electrometer_059kV_Num_0.txt"

    # get data and delete overflows
    [time_pet, data_pet] = delete_overflows(read_csv(file_pet, 12, 2), read_csv(file_pet, 12, 4))
    [time_pe, data_pe] = delete_overflows(read_csv(file_pe, 12, 2), read_csv(file_pe, 12, 4))
    [time_pvc, data_pvc] = delete_overflows(read_csv(file_pvc, 12, 2), read_csv(file_pvc, 12, 4))

    # format time (absolute time to seconds starting from zero)
    time_pet = format_time(time_pet)
    time_pe = format_time(time_pe)
    time_pvc = format_time(time_pvc)

    # make pdc shift
    [time_pol_pet, data_pol_pet, time_depol_pet, data_depol_pet] = pdc_shift(time_pet, data_pet)
    [time_pol_pe, data_pol_pe, time_depol_pe, data_depol_pe] = pdc_shift(time_pe, data_pe)
    [time_pol_pvc, data_pol_pvc, time_depol_pvc, data_depol_pvc] = pdc_shift(time_pvc, data_pvc)

    # fit pdc shift data to constant time intervals
    [time_pol_pet_fit, data_pol_pet_fit] = fit_data_to_time_list(time_pol_pet, data_pol_pet)
    [time_depol_pet_fit, data_depol_pet_fit] = fit_data_to_time_list(time_depol_pet, data_depol_pet)
    [time_pol_pe_fit, data_pol_pe_fit] = fit_data_to_time_list(time_pol_pe, data_pol_pe)
    [time_depol_pe_fit, data_depol_pe_fit] = fit_data_to_time_list(time_depol_pe, data_depol_pe)
    [time_pol_pvc_fit, data_pol_pvc_fit] = fit_data_to_time_list(time_pol_pvc, data_pol_pvc)
    [time_depol_pvc_fit, data_depol_pvc_fit] = fit_data_to_time_list(time_depol_pvc, data_depol_pvc)

    # pdc shift
    [time_pdc_pet, data_pdc_pet] = pdc_curve(time_pol_pet_fit, data_pol_pet_fit, time_depol_pet_fit,
                                             data_depol_pet_fit)
    [time_pdc_pe, data_pdc_pe] = pdc_curve(time_pol_pe_fit, data_pol_pe_fit, time_depol_pe_fit,
                                           data_depol_pe_fit)
    [time_pdc_pvc, data_pdc_pvc] = pdc_curve(time_pol_pvc_fit, data_pol_pvc_fit, time_depol_pvc_fit,
                                             data_depol_pvc_fit)

    # create plot for PET
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-4, 4])
    plt.plot(time_pol_pet, data_pol_pet, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_pet, data_depol_pet, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_pet_fit, data_pol_pet_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_pet_fit, data_depol_pet_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_pet, data_pdc_pet, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for PET (E = 50 kV/cm)")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_PET_50kVpercm.png", dpi=300)
    plt.show()

    # create plot for PE
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-30, 30])
    plt.plot(time_pol_pe, data_pol_pe, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_pe, data_depol_pe, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_pe_fit, data_pol_pe_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_pe_fit, data_depol_pe_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_pe, data_pdc_pe, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for PE (E = 50 kV/cm)")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_PE_50kVpercm.png", dpi=300)
    plt.show()

    # create plot for PVC
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-20, 30])
    plt.plot(time_pol_pvc, data_pol_pvc, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_pvc, data_depol_pvc, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_pvc_fit, data_pol_pvc_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_pvc_fit, data_depol_pvc_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_pvc, data_pdc_pvc, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for PVC (E = 50 kV/cm)")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_PVC_50kVpercm.png", dpi=300)
    plt.show()

    # create plot for PDC curves PET/PE/PVC
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([0, 20])
    plt.plot(time_pdc_pet, data_pdc_pet, "lightcoral", label="PET PDC", marker="d", mfc='None', markevery=3)
    plt.plot(time_pol_pet_fit, data_pol_pet_fit, "lightcoral", dashes=[3, 2], label="PET Polarization", marker="d",
             mfc='None', markevery=3)
    plt.plot(time_pdc_pe, data_pdc_pe, "orangered", label="PE PDC", marker="o", mfc='None', markevery=3)
    plt.plot(time_pol_pe_fit, data_pol_pe_fit, "orangered", dashes=[3, 2], label="PE Polarization", marker="o",
             mfc='None', markevery=3)
    plt.plot(time_pdc_pvc, data_pdc_pvc, "maroon", label="PVC PDC", marker="^", mfc='None', markevery=3)
    plt.plot(time_pol_pvc_fit, data_pol_pvc_fit, "maroon", dashes=[3, 2], label="PVC Polarization", marker="^",
             mfc='None', markevery=3)
    # plt.title("PDC current curve comparison for PET, PE, and PVC")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="upper right")
    plt.grid()
    plt.savefig("results_pdc_bulk_PDC_PET_PE_PVC_50kVpercm.png", dpi=300)
    plt.show()


def e_field_plot_epoxy():
    file_250 = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_epoxy_05mm_electrometer_250V_Num_1.txt"
    file_500 = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_epoxy_05mm_electrometer_500V.txt"
    file_1000 = "Z:/stud/eliasl/public/data/thesis_measurements/pdc_bulk_std_epoxy_05mm_electrometer_1000V_Num_1.txt"

    # get data and delete overflows
    [time_250, data_250] = delete_overflows(read_csv(file_250, 12, 2), read_csv(file_250, 12, 4))
    [time_500, data_500] = delete_overflows(read_csv(file_500, 12, 2), read_csv(file_500, 12, 4))
    [time_1000, data_1000] = delete_overflows(read_csv(file_1000, 12, 2), read_csv(file_1000, 12, 4))

    # format time (absolute time to seconds starting from zero)
    time_250 = format_time(time_250)
    time_500 = format_time(time_500)
    time_1000 = format_time(time_1000)

    # make pdc shift
    [time_pol_250, data_pol_250, time_depol_250, data_depol_250] = pdc_shift(time_250, data_250)
    [time_pol_500, data_pol_500, time_depol_500, data_depol_500] = pdc_shift(time_500, data_500)
    [time_pol_1000, data_pol_1000, time_depol_1000, data_depol_1000] = pdc_shift(time_1000, data_1000)

    # fit pdc shift data to constant time intervals
    [time_pol_250_fit, data_pol_250_fit] = fit_data_to_time_list(time_pol_250, data_pol_250)
    [time_depol_250_fit, data_depol_250_fit] = fit_data_to_time_list(time_depol_250, data_depol_250)
    [time_pol_500_fit, data_pol_500_fit] = fit_data_to_time_list(time_pol_500, data_pol_500)
    [time_depol_500_fit, data_depol_500_fit] = fit_data_to_time_list(time_depol_500, data_depol_500)
    [time_pol_1000_fit, data_pol_1000_fit] = fit_data_to_time_list(time_pol_1000, data_pol_1000)
    [time_depol_1000_fit, data_depol_1000_fit] = fit_data_to_time_list(time_depol_1000, data_depol_1000)

    # pdc shift
    [time_pdc_250, data_pdc_250] = pdc_curve(time_pol_250_fit, data_pol_250_fit, time_depol_250_fit,
                                             data_depol_250_fit)
    [time_pdc_500, data_pdc_500] = pdc_curve(time_pol_500_fit, data_pol_500_fit, time_depol_500_fit,
                                             data_depol_500_fit)
    [time_pdc_1000, data_pdc_1000] = pdc_curve(time_pol_1000_fit, data_pol_1000_fit, time_depol_1000_fit,
                                               data_depol_1000_fit)

    # create plot for 250
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-2, 2])
    plt.plot(time_pol_250, data_pol_250, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_250, data_depol_250, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_250_fit, data_pol_250_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_250_fit, data_depol_250_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_250, data_pdc_250, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for epoxy 250V")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_epoxy_250V.png", dpi=300)
    plt.show()

    # create plot for 500
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-5, 5])
    plt.plot(time_pol_500, data_pol_500, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_500, data_depol_500, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_500_fit, data_pol_500_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_500_fit, data_depol_500_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_500, data_pdc_500, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for epoxy 500")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_epoxy_500V.png", dpi=300)
    plt.show()

    # create plot for 1000
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-5, 5])
    plt.plot(time_pol_1000, data_pol_1000, "lightsteelblue", label="Polarization current raw data")
    plt.plot(time_depol_1000, data_depol_1000, "navajowhite", label="Depolarization current raw data")
    plt.plot(time_pol_1000_fit, data_pol_1000_fit, "navy", mfc='None', marker='o', markevery=5,
             label="Polarization current fitted data")
    plt.plot(time_depol_1000_fit, data_depol_1000_fit, "darkorange", mfc='None', marker='d', markevery=5,
             label="Depolarization current fitted data")
    plt.plot(time_pdc_1000, data_pdc_1000, "red", mfc='None', marker='^', markevery=5, label="PDC curve")
    plt.title("PDC measurement for epoxy 1000")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig("results_pdc_bulk_epoxy_1000V.png", dpi=300)
    plt.show()

    # create plot for PDC curves
    plt.rcParams["font.family"] = "Times New Roman"
    plt.ylim([-0.2, 1.5])
    plt.plot(time_pdc_250, data_pdc_250, "lightcoral", label="250 PDC", marker="d", mfc='None', markevery=3)
    plt.plot(time_pol_250_fit, data_pol_250_fit, "lightcoral", dashes=[3, 2], label="250 Polarization", marker="d",
             mfc='None', markevery=3)
    plt.plot(time_pdc_500, data_pdc_500, "orangered", label="PE PDC", marker="o", mfc='None', markevery=3)
    plt.plot(time_pol_500_fit, data_pol_500_fit, "orangered", dashes=[3, 2], label="PE Polarization", marker="o",
             mfc='None', markevery=3)
    plt.plot(time_pdc_1000, data_pdc_1000, "maroon", label="1000 PDC", marker="^", mfc='None', markevery=3)
    plt.plot(time_pol_1000_fit, data_pol_1000_fit, "maroon", dashes=[3, 2], label="1000 Polarization", marker="^",
             mfc='None', markevery=3)
    plt.title("PDC current curve comparison for 250, PE, and 1000")
    plt.xlabel("Time in s")
    plt.ylabel("Current in pA")
    plt.legend(loc="upper right")
    plt.grid()
    plt.savefig("results_pdc_bulk_PDC_epoxy_e_field_comparison.png", dpi=300)
    plt.show()


# material_plot_e_field_5()
# material_plot_e_field_50()
e_field_plot_epoxy()
