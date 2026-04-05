# ACP Message Types
# 8 message types for inter-agent communication

HEALTH_QUERY    = "HEALTH_QUERY"    # Request health assessment
HEALTH_RESULT   = "HEALTH_RESULT"   # Return health assessment
DRUG_VERIFY     = "DRUG_VERIFY"     # Request medication verification
DRUG_RESULT     = "DRUG_RESULT"     # Return verification result
CONTEXT_FETCH   = "CONTEXT_FETCH"   # Fetch patient context
CONTEXT_UPDATE  = "CONTEXT_UPDATE"  # Update patient context
POPULATION_PING = "POPULATION_PING" # Population health signal
LEARN_FEEDBACK  = "LEARN_FEEDBACK"  # Training feedback signal
