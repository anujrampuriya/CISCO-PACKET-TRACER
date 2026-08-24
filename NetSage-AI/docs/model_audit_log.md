# NetSage AI — Responsible AI Audit Log

This log records human review of AI-generated network diagnoses.

## Review Status

- Accepted: AI diagnosis was correct.
- Edited: AI diagnosis required correction by the human reviewer.
- Rejected: AI diagnosis was not accepted.

---

## Review Records

| Case ID | AI Diagnosis | Human Decision | Correction / Reason | Reviewer |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Agreement Summary

- Total reviewed: 5
- Accepted: 2
- Edited: 2
- Rejected: 1
- AI-Human agreement rate: 40.0%

## Responsible AI Notes

Human review is mandatory before accepting any AI-generated remediation.

AI-generated Cisco commands are recommendations only. They must be verified by a human before being applied to a network or Packet Tracer topology.

---

## Review: NET-001

- **Timestamp:** 2026-08-22 23:27:59
- **Decision:** Accepted
- **Reviewer:** Human reviewer
- **Reason:** AI diagnosis accepted without changes.

### AI Diagnosis

**Root Cause:** The router sub-interface GigabitEthernet0/0.10, which acts as the default gateway for PC1 in VLAN 10, is administratively down, preventing Inter-VLAN routing to reach Server1 in VLAN 30.

**OSI Layer:** Layer 3

**Confidence:** High

### Evidence

- GigabitEthernet0/0.10 is administratively down line protocol is down
- Rule R001 (INTERFACE_DOWN): An interface is administratively down.

**Verification Command:** `show ip interface GigabitEthernet0/0.10`

### Final Fix Steps

1. Enter global configuration mode using 'configure terminal'.
2. Navigate to the sub-interface using 'interface GigabitEthernet0/0.10'.
3. Enable the interface by running the 'no shutdown' command.
4. Verify that the sub-interface status changes to up/up using 'show ip interface brief'.


---

## Review: NET-005

- **Timestamp:** 2026-08-24 00:46:33
- **Decision:** Edited
- **Reviewer:** Human reviewer
- **Reason:** No additional reason provided.

### AI Diagnosis

**Root Cause:** The ACL (access‑list 101) contains a rule that explicitly denies TCP traffic from the Sales subnet (192.168.10.0/24) to the web server (10.0.0.10) on destination port 80, preventing HTTP connections.
The ACL should be reviewed to ensure that only the intended HTTP traffic is blocked and legitimate traffic is permitted.

**OSI Layer:** Layer 4

**Confidence:** High

### Evidence

- access-list 101 deny tcp 192.168.10.0 0.0.0.255 host 10.0.0.10 eq 80
- rule_checker finding: ACL_HTTP_BLOCKED – The ACL is blocking HTTP traffic on port 80.

**Verification Command:** `show access-lists 101`

### Final Fix Steps

1. 1. Enter configuration mode: `configure terminal`.
2. 2. Either remove the offending deny statement: `no access-list 101 deny tcp 192.168.10.0 0.0.0.255 host 10.0.0.10 eq 80`.
3. OR modify the ACL to permit HTTP before the deny line:
4. `access-list 101 permit tcp 192.168.10.0 0.0.0.255 host 10.0.0.10 eq 80`.
5. 3. Ensure the ACL order places the permit statement above any broader deny statements.
6. 4. Exit configuration mode and save: `end` then `write memory`.
7. 5. Verify the change with `show access-lists 101` and test connectivity from the Sales PC to the web server on port 80.


---

## Review: NET-006

- **Timestamp:** 2026-08-24 00:48:08
- **Decision:** Rejected
- **Reviewer:** Human reviewer
- **Reason:** The AI diagnosis is not sufficiently reliable for this case and requires further verification before remediation.

### AI Diagnosis

**Root Cause:** The NAT configuration on R1 lacks the overload keyword, so the router is performing static NAT without address translation pooling. Without NAT overload, only a single inside host can be translated, causing all internal PCs to fail reaching the external internet.

**OSI Layer:** Layer 3

**Confidence:** High

### Evidence

- show_outputs: ip nat inside source list 1 interface Gi0/1 (missing overload keyword)
- rule_checker finding: NAT_OVERLOAD_MISSING – NAT overload configuration is missing.

**Verification Command:** `show ip nat statistics`

### Final Fix Steps

1. 1. Verify the access‑list 1 definition includes the internal LAN subnet (e.g., access-list 1 permit 192.168.1.0 0.0.0.255).
2. 2. Modify the NAT statement to include overload: `ip nat inside source list 1 interface Gi0/1 overload`.
3. 3. (Optional) Add a NAT translation limit or PAT pool if multiple public addresses are needed.
4. 4. Save the configuration with `write memory` or `copy running-config startup-config`.
5. 5. Re‑test connectivity from an internal PC and verify NAT translations using `show ip nat translations`.


---

## Review: NET-008

- **Timestamp:** 2026-08-24 01:06:44
- **Decision:** Edited
- **Reviewer:** Human reviewer
- **Reason:** The AI identified the correct root cause, but the remediation steps were made more precise by explicitly adding VLAN 20 to the trunk allowed list and including verification of the change.

### AI Diagnosis

**Root Cause:** VLAN 20 is missing from the allowed VLAN list on the trunk link between SW1 and SW2. As a result, VLAN 20 traffic cannot traverse the trunk, causing connectivity failure for devices in VLAN 20.

**OSI Layer:** Layer 2

**Confidence:** High

### Evidence

- show_outputs: Switchport trunk allowed vlan 10 30 40 (VLAN 20 missing from allowed list)
- rule_checker finding: VLAN_NOT_ALLOWED_ON_TRUNK – Required VLAN is missing from the trunk allowed list.

**Verification Command:** `show interfaces trunk`

### Final Fix Steps

1. 1. Verify VLAN 20 exists on both switches using show vlan brief.
2. 2. Enter configuration mode on the affected trunk interface.
3. 3. Configure VLAN 20 on the trunk using switchport trunk allowed vlan add 20.
4. 4. Verify VLAN 20 appears in the trunk's allowed VLAN list using show interfaces trunk.
5. 5. Test connectivity between devices in VLAN 20.


---

## Review: NET-010

- **Timestamp:** 2026-08-24 01:07:03
- **Decision:** Accepted
- **Reviewer:** Human reviewer
- **Reason:** AI diagnosis accepted without changes.

### AI Diagnosis

**Root Cause:** The management SVI (VLAN 1) is administratively shut down, preventing any traffic to the switch's management IP (192.168.1.2) and making SSH unreachable.

**OSI Layer:** Layer 2

**Confidence:** High

### Evidence

- interface Vlan1; ip address 192.168.1.2 255.255.255.0; shutdown
- rule_checker finding: R010 – SVI_SHUTDOWN – The management SVI is administratively shut down.

**Verification Command:** `show ip interface brief | include Vlan1`

### Final Fix Steps

1. 1. Enter global configuration mode: `configure terminal`.
2. 2. Select the VLAN 1 interface: `interface vlan 1`.
3. 3. Enable the SVI: `no shutdown`.
4. 4. Verify the interface is up and has the correct IP: `show ip interface brief | include Vlan1`.
5. 5. Test SSH connectivity to 192.168.1.2 from a client.
