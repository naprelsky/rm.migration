# Main module

from flask import Flask, json, request
from utils.dumper import Dumper
from utils.migration import *

api = Flask(__name__)
g_dumper = Dumper()
g_migration: Migration = None


def migration_in_process() -> bool:
    return g_migration and g_migration.state == MigrationState.running


@api.route('/source', methods=['POST'])
def create_source_workload():
    """ Create new source workload """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    source_vm = g_dumper.read(Workload)
    if source_vm:
        error = "Source workload already exist. You can change it by PUT request."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()

    source_vm = Workload(body_json["ip"])
    source_vm.set_credentials(body_json["credentials"].get("username"),
                              body_json["credentials"].get("password"),
                              body_json["credentials"].get("domain"))
    for storage in body_json.get("storages"):
        point = MountPoint(storage)
        source_vm.storages.append(point)

    g_dumper.dump(source_vm)
    return json.dumps({"success": True}), 201


@api.route('/source', methods=['PUT'])
def edit_source_workload():
    """ Change source workload """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    source_vm = g_dumper.read(Workload)
    if not source_vm:
        error = "Source workload don't exist. You can create it by POST request."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()
    source_vm.set_credentials(body_json["credentials"].get("username"),
                              body_json["credentials"].get("password"),
                              body_json["credentials"].get("domain"))

    source_vm.storages.clear()
    for storage in body_json.get("storages"):
        point = MountPoint(storage)
        source_vm.storages.append(point)

    g_dumper.dump(source_vm)
    return json.dumps({"success": True}), 201


@api.route('/source', methods=['DELETE'])
def delete_source_workload():
    """ Delete source workload """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    g_dumper.delete(Workload)
    return json.dumps({"success": True}), 201


@api.route('/target', methods=['POST'])
def create_target_workload():
    """ Create new target workload """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    target_migration = g_dumper.read(MigrationTarget)
    if target_migration:
        error = "Source workload already exist. You can change it by PUT request."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()

    target_vm = Workload(body_json["target_vm"]["ip"])
    target_vm.set_credentials(body_json["target_vm"]["credentials"].get("username"),
                              body_json["target_vm"]["credentials"].get("password"),
                              body_json["target_vm"]["credentials"].get("domain"))
    for storage in body_json["target_vm"].get("storages"):
        point = MountPoint(storage)
        target_vm.storages.append(point)

    target_migration = MigrationTarget(body_json["cloud_type"])
    target_migration.set_cloud_credentials(body_json["cloud_credentials"].get("username"),
                                           body_json["cloud_credentials"].get("password"),
                                           body_json["cloud_credentials"].get("domain"))
    target_migration.target_vm = target_vm

    g_dumper.dump(target_migration)
    return json.dumps({"success": True}), 201


@api.route('/target', methods=['PUT'])
def edit_target_migration():
    """ Change target migration """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    target_migration = g_dumper.read(MigrationTarget)
    if not target_migration:
        error = "Target migration don't exist. You can create it by POST request."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()
    target_migration.cloud_type = body_json["cloud_type"]
    target_migration.set_cloud_credentials(body_json["cloud_credentials"].get("username"),
                                           body_json["cloud_credentials"].get("password"),
                                           body_json["cloud_credentials"].get("domain"))
    target_migration.target_vm.set_credentials(body_json["target_vm"]["credentials"].get("username"),
                                               body_json["target_vm"]["credentials"].get("password"),
                                               body_json["target_vm"]["credentials"].get("domain"))

    target_migration.target_vm.storages.clear()
    for storage in body_json["target_vm"].get("storages"):
        point = MountPoint(storage)
        target_migration.target_vm.storages.append(point)

    g_dumper.dump(target_migration)
    return json.dumps({"success": True}), 201


@api.route('/target', methods=['DELETE'])
def delete_target_migration():
    """ Delete target migration """

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    g_dumper.delete(MigrationTarget)
    return json.dumps({"success": True}), 201


@api.route('/migration', methods=['POST'])
def add_migration():

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    migration = g_dumper.read(Migration)
    if migration:
        error = "Migration already exist. You can change it by PUT request."
        return json.dumps({"error": error}), 500

    source_vm = g_dumper.read(Workload)
    if not source_vm:
        error = "Source VM is not selected or created."
        return json.dumps({"error": error}), 500

    target_migration = g_dumper.read(MigrationTarget)
    if not target_migration:
        error = "Target VM is not selected or created."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()

    mount_points = []
    for item in body_json["mount_points"]:
        mount_points.append(MountPoint(item))

    migration = Migration(mount_points, source_vm, target_migration)

    g_dumper.dump(migration)
    return json.dumps({"success": True}), 201


@api.route('/migration', methods=['PUT'])
def edit_migration():

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    migration = g_dumper.read(Migration)
    if not migration:
        error = "Migration don't exist. You can create it by POST request."
        return json.dumps({"error": error}), 500

    body_json = request.get_json()

    migration.source = g_dumper.read(Workload)
    migration.target = g_dumper.read(MigrationTarget)

    mount_points = []
    for item in body_json["mount_points"]:
        mount_points.append(MountPoint(item))
    migration.mount_points = mount_points

    g_dumper.dump(migration)
    return json.dumps({"success": True}), 201


@api.route('/migration', methods=['DELETE'])
def delete_migration():

    migration = g_dumper.read(Migration)
    if migration:
        migration.stop()

    g_dumper.delete(Migration)
    return json.dumps({"success": True}), 201


@api.route('/migration/run', methods=['POST'])
def run_migration():
    global g_migration

    if migration_in_process():
        error = "Changes prohibited during the migration process. Please wait for completion."
        return json.dumps({"error": error}), 500

    g_migration = g_dumper.read(Migration)
    if not g_migration:
        error = "Is required to create migration before run."
        return json.dumps({"error": error}), 500

    g_migration.run()
    return json.dumps({"success": True}), 201


@api.route('/migration/state', methods=['GET'])
def state_migration():
    global g_migration

    if not g_migration:
        error = "Migration is not created."
        return json.dumps({"error": error}), 500

    return json.dumps({"status": g_migration.state}), 201


if __name__ == "__main__":
    api.run(host='127.0.0.1', port=5000)
