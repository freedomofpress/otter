# otter
Infrastructure framework for Qubes-OS based testing on VMWare

The idea is to develop our own set of tools to automate as much as possible any SDW-related testing, while keeping the ability for interactive debugging sessions, results artifacts, GUI testing and so on.

The backend hypervisor is vmware ESX 7, that is so far the one that works best for nesting Qubes, but the project is structured in classes that would allow seamlessy plugging in another backend.
