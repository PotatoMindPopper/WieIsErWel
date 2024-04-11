# Description: Maakt een grafiek die aangeeft wie aanwezig is en wie niet
#
# :param attendance_list: Een lijst van Kamerleden die aanwezig waren
#



def create_chart(attendance_list):
    """
    Maakt een grafiek die aangeeft wie aanwezig is en wie niet

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    """
    # import matplotlib.pyplot as plt

    labels = ["Afwezig", "Aanwezig"]
    sizes = [150 - len(attendance_list), len(attendance_list)]
    colors = ["red", "green"]
    explode = (0.1, 0)  # explode 1st slice

    # plt.pie(
    #     sizes,
    #     explode=explode,
    #     labels=labels,
    #     colors=colors,
    #     autopct="%1.1f%%",
    #     shadow=True,
    #     startangle=140,
    # )
    # plt.axis("equal")
    # plt.show()
    
    # Gebruik numpy om de grafiek te maken
    import numpy as np
    import matplotlib.pyplot as plt
    
    _, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
    ax.axis("equal")
    # plt.show()


