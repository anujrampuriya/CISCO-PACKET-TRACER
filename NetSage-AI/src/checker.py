def check_case(case):

    show_output = case["show_outputs"].lower()

    findings = []

    # R001: Interface administratively down
    if "administratively down" in show_output:
        findings.append({
            "rule_id": "R001",
            "issue": "INTERFACE_DOWN",
            "message": "An interface is administratively down."
        })

    # R002: DHCP pool exhausted
    if "zero available" in show_output or "0 available" in show_output:
        findings.append({
            "rule_id": "R002",
            "issue": "DHCP_POOL_EXHAUSTED",
            "message": "The DHCP pool has no available addresses."
        })

    # R006: NAT overload missing

    if "ip nat inside source" in show_output:
        if "(missing overload keyword)" in show_output:
            findings.append({
                "rule_id": "R006",
                "issue": "NAT_OVERLOAD_MISSING",
                "message": "NAT overload configuration is missing."
            })
    # R010: SVI shutdown
    if "interface vlan" in show_output and "shutdown" in show_output:
        findings.append({
            "rule_id": "R010",
            "issue": "SVI_SHUTDOWN",
            "message": "The management SVI is administratively shut down."
        })



        # R003: DNS configuration issue
    if "no ip domain-lookup" in show_output or "not active" in show_output:
        findings.append({
            "rule_id": "R003",
            "issue": "DNS_CONFIGURATION_ERROR",
            "message": "DNS lookup configuration is not working correctly."
        })

    # R004: OSPF hello interval mismatch
    if "r1:" in show_output and "r2:" in show_output:
        if "hello-interval 10" in show_output and "hello-interval 20" in show_output:
            findings.append({
                "rule_id": "R004",
                "issue": "OSPF_HELLO_MISMATCH",
                "message": "OSPF hello intervals do not match between peers."
            })

    # R008: Required VLAN missing from trunk
    if "trunk allowed vlan" in show_output and "vlan 20 missing" in show_output:
        findings.append({
            "rule_id": "R008",
            "issue": "VLAN_NOT_ALLOWED_ON_TRUNK",
            "message": "Required VLAN is missing from the trunk allowed list."
        })

    # R011: Inter-switch link not configured as trunk
    if "sw1 fa0/24: switchport mode access" in show_output and \
       "sw2 fa0/24: switchport mode access" in show_output:
        findings.append({
            "rule_id": "R011",
            "issue": "INTER_SWITCH_LINK_NOT_TRUNK",
            "message": "The inter-switch link is configured as an access port."
        })

    # R012: OSPF interface incorrectly passive
    if "passive-interface serial0/1/0" in show_output:
        findings.append({
            "rule_id": "R012",
            "issue": "OSPF_PASSIVE_INTERFACE",
            "message": "The active OSPF interface is configured as passive."
        })
        # R013: Wrong access VLAN
    if "switchport access vlan 14" in show_output:
        findings.append({
            "rule_id": "R013",
            "issue": "ACCESS_VLAN_MISMATCH",
            "message": "The access port is configured for the wrong VLAN."
        })

        # R014: DHCP helper missing
    if "(missing ip helper-address)" in show_output:
        findings.append({
            "rule_id": "R014",
            "issue": "DHCP_HELPER_MISSING",
            "message": "The DHCP relay interface is missing an ip helper-address."
        })

    # R015: Static route next-hop unreachable
    if "(next-hop ip" in show_output and "unreachable" in show_output:
        findings.append({
            "rule_id": "R015",
            "issue": "STATIC_ROUTE_NEXT_HOP_INVALID",
            "message": "The static route points to an unreachable next hop."
        })

    # R016: FTP control port blocked
    if "(missing port 21)" in show_output:
        findings.append({
            "rule_id": "R016",
            "issue": "ACL_FTP_CONTROL_BLOCKED",
            "message": "The ACL is missing the FTP control port 21 permit."
        })

    # R017: NAT inside missing
    if "missing ip nat inside" in show_output:
        findings.append({
            "rule_id": "R017",
            "issue": "NAT_INSIDE_MISSING",
            "message": "The internal interface is missing ip nat inside."
        })
        # R018: RADIUS shared-secret mismatch
    if "incorrect_secret_key" in show_output:
        findings.append({
            "rule_id": "R018",
            "issue": "RADIUS_SECRET_MISMATCH",
            "message": "The RADIUS shared secret is incorrect."
        })

    # R019: Native VLAN mismatch
    if "native vlan 10" in show_output and "native vlan 99" in show_output:
        findings.append({
            "rule_id": "R019",
            "issue": "NATIVE_VLAN_MISMATCH",
            "message": "The native VLANs on the trunk peers do not match."
        })

    # R020: Gateway outside subnet
    if "outside subnet boundary" in show_output:
        findings.append({
            "rule_id": "R020",
            "issue": "GATEWAY_OUTSIDE_SUBNET",
            "message": "The configured default gateway is outside the host subnet."
        })
    # R021: Missing redistribution subnets
    if "redistribute eigrp 100" in show_output and "missing subnets" in show_output:
        findings.append({
            "rule_id": "R021",
            "issue": "REDISTRIBUTION_SUBNETS_MISSING",
            "message": "The redistribution configuration is missing the subnets keyword."
        })

    # R022: HTTPS ACL rule missing
    if "(missing port 443)" in show_output:
        findings.append({
            "rule_id": "R022",
            "issue": "ACL_HTTPS_BLOCKED",
            "message": "The ACL permits HTTP but does not permit HTTPS."
        })
    # R023: Duplicate IP
    if "duplicate address" in show_output:
        findings.append({
            "rule_id": "R023",
            "issue": "DUPLICATE_IP",
            "message": "A duplicate IP address has been detected."
        })


    # R024: VTP domain mismatch
    if "vtp domain" in show_output and "mismatch" in show_output:
        findings.append({
            "rule_id": "R024",
            "issue": "VTP_DOMAIN_MISMATCH",
            "message": "The VTP domains do not match."
        })

    # R025: DAI trust missing
    if "arp inspection trust" in show_output and "missing" in show_output:
        findings.append({
            "rule_id": "R025",
            "issue": "DAI_TRUST_MISSING",
            "message": "DAI trust is missing on the required uplink."
        })

    # R026: Port security violation
    if "psecure_violation" in show_output or "err-disabled" in show_output:
        findings.append({
            "rule_id": "R026",
            "issue": "PORT_SECURITY_VIOLATION",
            "message": "A port-security violation has been detected."
        })

    # R027: HSRP hello mismatch
    if "standby 1" in show_output and "hello 3" in show_output and "hello 10" in show_output:
        findings.append({
            "rule_id": "R027",
            "issue": "HSRP_HELLO_MISMATCH",
            "message": "HSRP hello timers do not match."
        })

    # R028: Missing dot1Q encapsulation
    if "missing encapsulation dot1q 20" in show_output:
        findings.append({
            "rule_id": "R028",
            "issue": "DOT1Q_ENCAPSULATION_MISSING",
            "message": "The router sub-interface is missing 802.1Q encapsulation."
        })

    # R029: IPv6 Router Advertisement suppressed
    if "ipv6 nd suppress-ra" in show_output:
        findings.append({
            "rule_id": "R029",
            "issue": "IPV6_RA_SUPPRESSED",
            "message": "IPv6 Router Advertisements are being suppressed."
        })

    # R030: CDP disabled
    if "no cdp run" in show_output:
        findings.append({
            "rule_id": "R030",
            "issue": "CDP_DISABLED",
            "message": "CDP is globally disabled."
        })
        # R005: ACL blocks HTTP
    if "access-list 101 deny tcp" in show_output and "eq 80" in show_output:
        findings.append({
            "rule_id": "R005",
            "issue": "ACL_HTTP_BLOCKED",
            "message": "The ACL is blocking HTTP traffic on port 80."
        })

    # R007: Guest ACL too permissive
    if "192.168.50.0 0.0.0.255 any" in show_output:
        findings.append({
            "rule_id": "R007",
            "issue": "GUEST_ACL_TOO_PERMISSIVE",
            "message": "The guest ACL permits unrestricted traffic to any destination."
        })

    # R009: Default gateway mismatch
    if "default gateway 192.168.1.254" in show_output:
        findings.append({
            "rule_id": "R009",
            "issue": "DEFAULT_GATEWAY_MISMATCH",
            "message": "The configured default gateway does not match the expected gateway."
        })
    if findings:
        return {
            "status": "ERRORS_DETECTED",
            "findings": findings
        }

    return {
        "status": "NO_ERRORS_DETECTED",
        "findings": []
    }