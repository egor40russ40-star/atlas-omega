from omega_resilience.domain.models import ServiceDescriptor, ServiceClass

def default_services():
    return [
        ServiceDescriptor("omega-safety",ServiceClass.CRITICAL,(),False,True),
        ServiceDescriptor("omega-risk",ServiceClass.CRITICAL,("omega-safety",),False,True),
        ServiceDescriptor("omega-capital",ServiceClass.CRITICAL,("omega-risk",),False,True),
        ServiceDescriptor("omega-broker-state",ServiceClass.CRITICAL,(),False,True),
        ServiceDescriptor("omega-market-data",ServiceClass.CRITICAL,(),True,True),
        ServiceDescriptor("omega-execution",ServiceClass.CRITICAL,("omega-safety","omega-risk","omega-capital","omega-broker-state"),False,True),
        ServiceDescriptor("omega-brain",ServiceClass.IMPORTANT,("omega-market-data",),True,False),
        ServiceDescriptor("omega-strategies",ServiceClass.IMPORTANT,("omega-brain",),True,False),
        ServiceDescriptor("omega-treasury",ServiceClass.IMPORTANT,("omega-broker-state",),True,False),
        ServiceDescriptor("omega-recorder",ServiceClass.IMPORTANT,(),True,False),
        ServiceDescriptor("omega-dashboard",ServiceClass.NONCRITICAL,(),True,False),
        ServiceDescriptor("omega-news",ServiceClass.NONCRITICAL,(),True,False),
        ServiceDescriptor("omega-research",ServiceClass.NONCRITICAL,(),True,False),
        ServiceDescriptor("omega-replay",ServiceClass.NONCRITICAL,(),True,False),
        ServiceDescriptor("omega-ai-lab",ServiceClass.NONCRITICAL,(),True,False),
    ]
