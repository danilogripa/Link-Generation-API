import urllib.parse

from urllib.parse import urlparse
def parse_link(link: str) -> dict:
    parsed_link = urlparse(link)
    return urllib.parse.parse_qs(parsed_link.query)

def build_final_query(af_query: dict, tg_query: dict, key_query: dict, agency: str) -> dict:
    final_query = {"app_id": tg_query["app_id"][0], "agency_id": tg_query["partner_id"][0]}

    if agency == "yes":
        final_query["source_id"] = af_query["pid"][0]
    else:
        final_query["partner_id"] = tg_query["partner_id"][0]

    final_query["tg_ver"] = tg_query["tg_ver"][0]

    for param in af_query:
        for kparam in key_query:
            if param == kparam:
                fparam = key_query[kparam][0].replace("{", "").replace("}", "")
                final_query[fparam] = af_query[param][0]

    for param in af_query:
        if param not in key_query:
            x_param = "x_" + param
            final_query[x_param] = af_query[param][0]

    return final_query

def handle_imp_type(final_query: dict, tg_query: dict) -> dict:
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

    return final_query

def handle_os_specific(final_query: dict, os: str) -> dict:
    if os == "ios" and "aaid" in final_query:
        del final_query["aaid"]

    if os == "android" and "idfa" in final_query:
        del final_query["idfa"]

    return final_query

def handle_redirect(final_query: dict, af_query: dict) -> dict:
    if "x_af_r" in final_query:
        final_query["x_af_r"] = urllib.parse.quote(af_query["af_r"][0], safe="")

    return final_query

def handle_trk_type(final_query: dict, tg_query: dict, red: str) -> dict:
    if red == "yes":
        if "token" in final_query:
            del final_query["token"]
    else:
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

    return final_query

def build(red: None, af_link: str, tg_link: str, key_link: str, os: str, agency: str, typeT: str) -> str:
    af_query = parse_link(af_link)
    tg_query = parse_link(tg_link)
    key_query = parse_link(key_link)

    final_query = build_final_query(af_query, tg_query, key_query, agency)

    if typeT == "imp":
        final_query = handle_imp_type(final_query, tg_query)

    final_query = handle_os_specific(final_query, os)
    final_query = handle_redirect(final_query, af_query)

    if typeT == "trk":
        final_query = handle_trk_type(final_query, tg_query, red)
        paths2s = "s2s" if red == "no" else tg_link.path
    else:
        paths2s = tg_link.path

    end_query = '&'.join('{}={}'.format(k, v) for k, v in final_query.items())
    final_link = tg_link.scheme + "://" + tg_link.netloc + "/" + paths2s + "?" + tg_link.params + end_query

    return final_link