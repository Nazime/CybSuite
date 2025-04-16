# Quickstart

In this example, assume there are 10 Windows servers and workstations to review. The first step is to obtain the extraction script. This can either be generated using the `cybs-review CLI` or downloaded from the GitHub repository [URL].

```bash
# Get the extraction script from the CLI
cybs-review script windows > extract_windows.ps1
```

Next, run the script on each server. It should be executed with **administrator privileges** to extract all configuration. It can also be executed with **limited privileges**, but with less configuration extracted, and could be used to identify **potential privilege escalation paths**.


```powershell
# To be run on each Windows server (preferably as admin)
./extract_windows.ps1
```

On the system where Cybs-Review is installed, create a new workspace, in this example named `windows_audit`:

```bash
cybs-review new windows_audit
```

Copy all the generated files into the "extracts" folder within the new workspace. Then, review the extracted data:

```bash
cybs-review review windows_audit
```
