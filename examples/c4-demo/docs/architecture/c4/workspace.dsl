workspace "Claims Platform" "Internal platform managing the claim lifecycle from submission to disbursement" {

    // ─────────────────────────────────────────────────────────────────
    // MODEL — Claims Platform demo
    //
    // This workspace exercises all four arch-c4 modes:
    //   • context     (§3) — SYS-01 + actors + external systems
    //   • container   (§5.1) — 5 containers inside SYS-01
    //   • component   (§5.2) — drill into CON-02 Claims API
    //   • deployment  (§7) — production environment
    //
    // Identifiers follow the kit convention:
    //   SYS_NN, CON_NN, CMP_NN, DN_NN  (DSL identifier)
    //   "SYS-NN — Name"                (display name)
    // ─────────────────────────────────────────────────────────────────

    model {

        // ── Actors (people) ─────────────────────────────────────────
        P_01 = person "P-01 — Claims Handler" "Insurance employee triaging claims" {
            tags "internal"
        }

        P_02 = person "P-02 — Customer" "Policyholder submitting a claim" {
            tags "external"
        }

        // ── Primary software system being documented ───────────────
        SYS_01 = softwareSystem "SYS-01 — Claims Platform" "Manages the claim lifecycle from submission to disbursement" {
            tags "core"

            // ── Containers (arc42 §5.1) ─────────────────────────
            CON_01 = container "CON-01 — Customer Portal" "Self-service claim submission UI" "React 18 + Vite" {
                tags "web"
            }

            CON_02 = container "CON-02 — Claims API" "Domain command + query surface" "Node.js 20 + Fastify" {
                tags "core"

                // ── Components inside CON-02 (arc42 §5.2) ───
                CMP_01 = component "CMP-01 — Submit Claim Endpoint" "HTTP POST /claims handler" "Fastify route" {
                    tags "endpoint"
                    properties {
                        "implements" "none"
                        "code-path" "src/claims/http/SubmitClaimRoute.ts"
                    }
                }

                CMP_02 = component "CMP-02 — Claim Command Handler" "Translates HTTP into domain commands on Claim aggregate" "TypeScript command bus" {
                    tags "core"
                    properties {
                        "implements" "BC-01.AGG-02"
                        "code-path" "src/claims/application/ClaimCommandHandler.ts"
                    }
                }

                CMP_03 = component "CMP-03 — Claim Aggregate Repository" "Loads and persists Claim aggregate state" "TypeORM" {
                    tags "persistence"
                    properties {
                        "implements" "BC-01.AGG-02"
                        "code-path" "src/claims/infrastructure/ClaimRepository.ts"
                    }
                }

                CMP_04 = component "CMP-04 — Claim Event Publisher" "Publishes ClaimSubmitted, ClaimApproved to Kafka" "kafkajs" {
                    tags "core"
                    properties {
                        "implements" "BC-01.AGG-02"
                        "code-path" "src/claims/infrastructure/ClaimEventPublisher.ts"
                    }
                }
            }

            CON_03 = container "CON-03 — Claims Database" "Persistent state for Claim aggregate" "PostgreSQL 16" {
                tags "database"
            }

            CON_04 = container "CON-04 — Event Bus" "Domain event distribution" "Kafka 3.7" {
                tags "queue"
            }

            CON_05 = container "CON-05 — Notification Service" "Outbound email + SMS" "Node.js 20" {
                tags "core"
            }
        }

        // ── External systems ────────────────────────────────────────
        SYS_02 = softwareSystem "SYS-02 — Payment Gateway" "Third-party disbursement provider" {
            tags "external"
        }

        SYS_03 = softwareSystem "SYS-03 — Identity Provider" "Corporate SSO (Azure AD)" {
            tags "external"
        }

        // ── Relationships (declare AFTER all referenced identifiers) ─
        // Actor to system
        P_01 -> SYS_01 "Triages claims via" "HTTPS/Web UI"
        P_02 -> SYS_01 "Submits claims via" "HTTPS/Web UI"

        // Inside the system (containers)
        CON_01 -> CON_02 "Sends claim commands to" "HTTPS/JSON"
        CON_02 -> CON_03 "Reads from + writes to" "SQL/TCP"
        CON_02 -> CON_04 "Publishes domain events to" "Kafka protocol"
        CON_05 -> CON_04 "Consumes events from" "Kafka protocol"

        // Inside CON-02 (components)
        CMP_01 -> CMP_02 "Dispatches command via" ""
        CMP_02 -> CMP_03 "Loads + saves aggregates via" ""
        CMP_02 -> CMP_04 "Publishes events via" ""

        // System to external systems
        CON_02 -> SYS_02 "Initiates disbursement via" "HTTPS/JSON"
        CON_02 -> SYS_03 "Authenticates via" "OIDC"
        CON_01 -> SYS_03 "Authenticates via" "OIDC"

        // ── Deployment environment (arc42 §7) ───────────────────────
        deploymentEnvironment "Production" {

            DN_01 = deploymentNode "DN-01 — AWS eu-west-1" "Primary region" {

                DN_02 = deploymentNode "DN-02 — Production Kubernetes" "EKS 1.30" {
                    tags "kubernetes"

                    CON_02_INSTANCE = containerInstance CON_02 {
                        tags "primary"
                    }

                    CON_05_INSTANCE = containerInstance CON_05
                }

                DN_03 = deploymentNode "DN-03 — RDS for PostgreSQL" "AWS RDS Multi-AZ" {
                    tags "managed-database"
                    CON_03_INSTANCE = containerInstance CON_03
                }

                DN_04 = deploymentNode "DN-04 — MSK" "AWS Managed Streaming for Kafka, 3 brokers" {
                    tags "managed-queue"
                    CON_04_INSTANCE = containerInstance CON_04
                }

                DN_05 = deploymentNode "DN-05 — CloudFront" "Global edge cache" {
                    tags "cdn"
                    CON_01_INSTANCE = containerInstance CON_01
                }
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────
    // VIEWS
    // ─────────────────────────────────────────────────────────────────

    views {

        systemContext SYS_01 "systemContext" {
            include *
            autolayout lr
            description "SYS-01 — System Context (arc42 §3)."
        }

        container SYS_01 "containers" {
            include *
            autolayout lr
            description "SYS-01 — Containers (arc42 §5.1)."
        }

        component CON_02 "components-CON-02" {
            include *
            autolayout lr
            description "CON-02 internal components (arc42 §5.2)."
        }

        deployment SYS_01 "Production" "deployment-production" {
            include *
            autolayout lr
            description "SYS-01 — Production deployment (arc42 §7.x)."
        }

        styles {
            element "Person" {
                shape Person
                background "#08427B"
                color "#ffffff"
            }
            element "Software System" {
                background "#1168BD"
                color "#ffffff"
            }
            element "Container" {
                background "#438DD5"
                color "#ffffff"
            }
            element "Component" {
                background "#85BBF0"
                color "#000000"
            }
            element "external" {
                background "#999999"
                color "#ffffff"
            }
            element "core" {
                background "#0B6FB8"
                color "#ffffff"
            }
            element "database" {
                shape Cylinder
            }
            element "queue" {
                shape Pipe
            }
            element "web" {
                shape WebBrowser
            }
            element "mobile" {
                shape MobileDeviceLandscape
            }
        }

        // theme default omitted — fetches from cloud service that EOLs 2026-09-30
    }
}
