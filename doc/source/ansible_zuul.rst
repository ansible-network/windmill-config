:title: Zuul

Zuul
####

Zuul is a pipeline-oriented project gating system.  It facilitates
running tests and automated tasks in response to Code Review events.

At a Glance
===========

:Hosts:
  * https://dashboard.zuul.ansible.com/
  * https://uptime.zuul.ansible.com/
:Windmill:
  * https://opendev.org/windmill
  * https://opendev.org/windmill/windmill-config
:Configuration:
  * `zuul/main.yaml`
  * `zuul.d`
:Projects:
  * https://opendev.org/zuul/zuul
  * https://github.com/ansible/ansible-zuul-jobs
  * https://github.com/ansible/project-config
:Bugs:
  * https://storyboard.openstack.org/#!/project/679
:Resources:
  * `Zuul Reference Manual <https://docs.openstack.org/infra/zuul>`_
:Chat:
  * #zuul on freenode

Overview
========

The Ansible project uses a number of pipelines in Zuul:

**check**
  Newly uploaded patchsets enter this pipeline to receive an initial result on
  GitHub.

**gate**
  Changes that have been approved by core reviewers are enqueued in
  order in this pipeline, and if they pass tests, will be merged.

**post**
  This pipeline runs jobs that operate after each change is merged.

**pre-release**
  This pipeline runs jobs on projects in response to pre-release tags.

**release**
  When a commit is tagged as a release, this pipeline runs jobs that
  publish archives and documentation.

**silent**
  This pipeline is used for silently testing new jobs.

**experimental**
  This pipeline is used for on-demand testing of new jobs.

**periodic**
  This pipeline has jobs triggered on a timer for e.g. testing for
  environmental changes daily.

Zuul watches events in GitHub and matches those events to the pipelines above.
If a match is found, it adds the change to the pipeline and starts running
related jobs.

The **gate** pipeline uses speculative execution to improve
throughput.  Changes are tested in parallel under the assumption that
changes ahead in the queue will merge.  If they do not, Zuul will
abort and restart tests without the affected changes.  This means that
many changes may be tested in parallel while continuing to assure that
each commit is correctly tested.

Zuul's current status may be viewed at
`<https://dashboard.zuul.ansible.com/>`_.

Zuul's configuration is stored in `zuul/main.yaml`.  Anyone
may propose a change to the configuration by editing that file and
submitting the change to Gerrit for review.

For the full syntax of Zuul's configuration file format, see the `Zuul
reference manual <https://docs.openstack.org/infra/zuul>`_.


Ansible Zuul Hosts
==================

.. table:: **Ansible Zuul Hosts**

  =========================================  ========  =================
  Host                                       Provider  Role
  =========================================  ========  =================
  bastion01.sjc1.vexxhost.zuul.ansible.com   vexxhost  Bastion Node
  borg01.ca-ymq-1.vexxhost.zuul.ansible.com  vexxhost  Borg Backups
  db01.sjc1.vexxhost.zuul.ansible.com        vexxhost  DiskImage Builder
  nb01.sjc1.vexxhost.zuul.ansible.com        vexxhost  Nodepool Builder
  nb02.sjc1.vexxhost.zuul.ansible.com        vexxhost  Nodepool Builder
  nl01.sjc1.vexxhost.zuul.ansible.com        vexxhost  Nodepool Launcher
  nl02.sjc1.vexxhost.zuul.ansible.com        vexxhost  Nodepool launcher
  statsd01.sjc1.vexxhost.zuul.ansible.com    vexxhost  Zuul Executor
  ze01.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Executor
  ze02.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Executor
  ze03.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Executor
  zk01.sjc1.vexxhost.zuul.ansible.com        vexxhost  ZooKeeper Node
  zk02.sjc1.vexxhost.zuul.ansible.com        vexxhost  ZooKeeper Node
  zk03.sjc1.vexxhost.zuul.ansible.com        vexxhost  ZooKeeper Node
  zm01.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Merger
  zm02.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Merger
  zs01.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Scheduler
  zs02.sjc1.vexxhost.zuul.ansible.com        vexxhost  Zuul Scheduler
  =========================================  ========  =================

.. note:: Where is zuul web?

Sysadmin
========

Zuul has four main subsystems:

* Zuul Scheduler
* Zuul Executors
* Zuul Mergers
* Zuul Web

that in OpenStack's deployment depend on four 'external' systems:

* Nodepool
* Zookeeper
* gear
* MariaDB

Scheduler
---------

The Zuul Scheduler and gear are all co-located on a single host,
referred to by the ``zuul.openstack.org`` CNAME in DNS.

Zuul is stateless, so the server does not need backing up. However
zuul talks through git and ssh so you will need to manually check ssh
host keys as the zuul user.

.. note::  Could we use speak about Ansible Zuul's scheduler and merger?

e.g.::

  sudo su - zuul
  ssh -p 29418 dashboard.zuul.ansible.com

The Zuul Scheduler talks to Nodepool using Zookeeper and distributes work to
the executors using gear.

Ansible's Zuul installation is also configured to write job results into
a MySQL database via the SQL Reporter plugin. The database for that is a
Rackspace Cloud DB and is configured in the ``mysql`` entry of the
``zuul_connection_secrets`` entry for the ``zuul-scheduler`` group.

Restarting the Scheduler
------------------------

Zuul Scheduler restarts are disruptive, so non-emergency restarts should
always be scheduled for quieter times of the day, week and cycle. To be as
courteous to developers as possible, just prior to a restart the `Zuul
Status Page`_ should be checked to see the status of the gate. If there is a
series of changes nearly merged, wait until that has been completed.

Since Zuul is stateless, some work needs to be done to save and then
re-enqueue patches when restarts are done. To accomplish this, start by
running `zuul-changes.py
<https://opendev.org/zuul/zuul/src/branch/master/tools/zuul-changes.py>`_
to save the check and gate queues::

  python /opt/zuul/tools/zuul-changes.py http://zuul.openstack.org \
    check >check.sh
  python /opt/zuul/tools/zuul-changes.py http://zuul.openstack.org \
    gate >gate.sh

.. note:: Document where is this done on Ansible Zuul, also zuul-cli

These check.sh and gate.sh scripts will be used after the restart to
re-enqueue the changes.

Now use `service zuul stop` to stop zuul and then run ps to make sure
the process has actually stopped, it may take several seconds for it to
finally go away.

Once you're ready, use `service zuul start` to start zuul again.

To re-enqueue saved jobs, first run the gate.sh script and then check.sh to
re-enqueue the changes from before the restart::

  ./gate.sh
  ./check.sh

You may watch the `Zuul Status Page`_ to confirm that changes are
returning to the queues.

Executors
---------

The Zuul Executors are a horizontally scalable set of servers named
ze*.openstack.org. They perform git merging operations for the scheduler
and execute Ansible playbooks to actually run jobs.

Our jobs are configured to upload as much information as possible along with
their logs, but if there is an error which can not be diagnosed in that
manner, logs are available in the executor-debug log file on
the executor host.  You may use the Zuul build UUID to track
assignment of a given job from the Zuul scheduler to the Zuul executor
used by that job.

It is safe, although not free, to restart executors. If an executor goes away
the scheduler will reschedule the jobs it was originally running.

Web
---

Zuul Web is a horizontally scalable service. It is currently running colocated
with the scheduler on zuul.openstack.org. Zuul Web provides live console
streaming and will be the home of various web dashboards such as the status
page.

Zuul Web is stateless so is safe to restart, however restarting it will result
in a loss of connection for anyone watching a live-stream of a console log
when the restart happens.

Zuul Ops
========

Zuul Client
-----------

Zuul includes a simple command line client that may be used to affect Zuul’s
behavior while running. It must be run on a host that has access to the
Gearman server (e.g., locally on the Zuul host), or on a host with access to
Zuul’s web server.

You can check further info on the documentation at
`<https://zuul-ci.org/docs/zuul/user/client-user.html>`_.


Ansible Zuul Ops
----------------

Hold a node
^^^^^^^^^^^

Restart Nodepool
^^^^^^^^^^^^^^^^

Restart Zuul
^^^^^^^^^^^^

Create a job
^^^^^^^^^^^^

Create a flavor
^^^^^^^^^^^^^^^

Change a job settings
^^^^^^^^^^^^^^^^^^^^^

.. note::

  This are just some ideas on sections for the documentation, but more might be
  added.

.. _zuul_github_projects:

GitHub Projects
===============

OpenStack does not use GitHub for development purposes, but there are some
non-OpenStack projects in the broader ecosystem that we care about who do.
When we are interested in setting up jobs in Zuul to test the interaction
between OpenStack projects and those ecosystem projects, we can add the
OpenDev Zuul GitHub app to those projects, then configure them in Zuul.

In order to add the GitHub app to a project, an admin on that project should
navigate to the `OpenDev Zuul`_ app in the GitHub UI. From there they can
click "Install", then choose the project or organization they want to install
the App on.

The repository then needs to be added to the `zuul/main.yaml` file before Zuul
can be configured to actually run jobs on it.

.. _OpenDev Zuul: https://github.com/apps/opendev-zuul
.. _Zuul Reference Manual: https://docs.openstack.org/infra/zuul
.. _Zuul Status Page: http://zuul.openstack.org
