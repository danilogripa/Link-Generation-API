import urllib.parse

from urllib.parse import urlparse


def build(red: None, af_link: str, tg_link: str, key_link: str, os: str, agency: str, typeT: str) -> str:
    # Get AppsFlyer Link and break into parameters
    af_link = urlparse(af_link)
    af_query = urllib.parse.parse_qs(af_link.query)

    # Get TrafficGuard Link and break into parameters
    tg_link = urlparse(tg_link)
    tg_query = urllib.parse.parse_qs(tg_link.query)

    # Get Key Link and break into parameters
    key_link = urlparse(key_link)
    key_query = urllib.parse.parse_qs(key_link.query)

    #########################################
    #########################################

    final_query = {"app_id": tg_query["app_id"][0], "agency_id": tg_query["partner_id"][0]}

    # adding partner_id
    if agency == "yes":
        final_query["source_id"] = af_query["pid"][0]
    else:
        final_query["partner_id"] = tg_query["partner_id"][0]

    # adding tg_ver
    final_query["tg_ver"] = tg_query["tg_ver"][0]

    # adding parameters from the Key
    for param in af_query:
        for kparam in key_query:
            if param == kparam:
                fparam = key_query[kparam][0].replace("{", "")
                fparam = fparam.replace("}", "")
                final_query[fparam] = af_query[param][0]

    # adding what is missing with x_ parameters
    for param in af_query:
        if param not in key_query:
            x_param = "x_" + param
            final_query[x_param] = af_query[param][0]

    # only for imps
    # adding UA
    if typeT == "imp":
        if "user_agent" not in final_query and "ip_address" not in final_query:
            final_query["user_agent"] = "#USER_AGENT_MACRO#"
            final_query["ip_address"] = "#IP_ADDRESS_MACRO#"

        if "x_af_ip" in final_query and "x_af_ua" in final_query:
            final_query["user_agent"] = final_query["x_af_ua"]
            final_query["ip_address"] = final_query["x_af_ip"]
            del final_query["x_af_ip"]
            del final_query["x_af_ua"]

        if "token" not in final_query and "token" in tg_query:
            final_query["token"] = tg_query["token"][0]

    # Checking for URL redirect and encoding it
    if "x_af_r" in final_query:
        final_query["x_af_r"] = urllib.parse.quote(af_query["af_r"][0], safe="")

    # removing aaid from IOS links (if exists)
    if (os == "ios") and ("aaid" in final_query):
        del final_query["aaid"]

    # removing idfa from Android links (if exists)
    if (os == "android") and ("idfa" in final_query):
        del final_query["idfa"]

    # last changes if trk link + standard redirect
    if (red == "yes") and (typeT == "trk"):
        # remove token if exists
        if "token" in final_query:
            del final_query["token"]

    # last changes if trk link + S2S
    if (red == "no") and (typeT == "trk"):
        paths2s = "s2s"

        if "user_agent" not in final_query and "ip_address" not in final_query:
            final_query["user_agent"] = "#USER_AGENT_MACRO#"
            final_query["ip_address"] = "#IP_ADDRESS_MACRO#"

        if "x_af_ip" in final_query and "x_af_ua" in final_query:
            final_query["user_agent"] = final_query["x_af_ua"]
            final_query["ip_address"] = final_query["x_af_ip"]
            del final_query["x_af_ip"]
            del final_query["x_af_ua"]

        if "token" not in final_query:
            if "token" in tg_query:
                final_query["token"] = tg_query["token"][0]
            else:
                final_query["token"] = "#MISSING_TOKEN#"
    else:
        paths2s = tg_link.path

        # last changes if imp link + standard Redirect
        # if(typeT == "imp"):

    end_query = '&'.join('{}={}'.format(k, v) for k, v in final_query.items())
    final_link = tg_link.scheme + "://" + tg_link.netloc + "/" + paths2s + "?" + tg_link.params + end_query

    return final_link
