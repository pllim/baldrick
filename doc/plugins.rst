Available plugins and configuration
===================================

This page lists the available plugins. Note that to enable a plugin, your bot
app should include an ``enabled = true`` entry in the ``pyproject.toml`` file
under the section for the specific plugin.

CircleCI Artifacts
------------------

The CircleCI service provides the option of `storing build artifacts
<https://circleci.com/docs/2.0/artifacts/>`_. The baldrick plugin will
automatically post the link to the artifacts as a status check in a GitHub pull
request to avoid having to click through multiple pages to find the link to the
artifacts. To enable this plugin, include the following in your
``pyproject.toml`` file::

    [ tool.<your-bot-name>.circleci_artifacts ]
    enabled = true

You can then include additional sub-sections in the configuration for each
set of artifacts, for example::

    [ tool.<your-bot-name>.circleci_artifacts.sphinx ]
    url = "html/index.html"
    message = "This is the documentation"

The ``url`` item should be set to the file path of the artifacts, and the
message is what will be shown in the status check.

Push handlers
-------------

We provide a plugin that will perform custom actions whenever a push is made to
a repository, whether to a branch or a tag.

To enable pull request handlers, include the following in your
``pyproject.toml`` file::

    [ tool.<your-bot-name>.pushes ]
    enabled = true

If you want to write your own custom handler, import
``push_handler`` from baldrick as follows::

    from baldrick.plugins.github_pushes import push_handler

then use it to decorate a function of the form::

    @push_handler
    def do_something_on_push(repo_handler, git_ref):
        ...

This function will be called with ``repo_handler``, an instance of
:class:`~baldrick.github.github_api.RepoHandler` (click on
the class names to find out the available properties/methods), and ``git_ref``
which will be a string containing the ref for the push (e.g.
``refs/heads/master``). If the ``git_ref`` is a branch, ``repo_handler.branch``
will be correctly set, but note that the ``git_ref`` could also point to a tag.

Pull request handlers
---------------------

We provide a plugin that will perform checks on a pull request and report the
results back to the pull request using status checks. Which checks are done are
themselves plugins and will be described in subsequent sections.

To enable pull request handlers, include the following in your
``pyproject.toml`` file::

    [ tool.<your-bot-name>.pull_requests ]
    enabled = true

In addition, you can use the following configuration items if you wish to change
the default behavior:

* ``skip_labels = []``: this can be set to a list of GitHub labels which, if
  present, will cause the checks to be skipped. Note that labels are
  case-sensitive. The default is an empty list.

* ``skip_fails = false/true``: if ``true``, if the checks are skipped due to
  ``skip_labels``, then a failed status check will be posted to the pull request.
  If ``false``, the checks will be silently skipped. The default is ``true``.

GitHub milestone checker
^^^^^^^^^^^^^^^^^^^^^^^^

This pull request handler plugin checks whether the milestone has been
set. To enable this plugin, include the following in your ``pyproject.toml``
file::

    [ tool.<your-bot-name>.milestones ]
    enabled = true

If you wish to customize the message shown in the results of the check, you can
use the ``missing_message = "..."`` and ``present_message = "..."`` configuration
items.

Towncrier changelog checker
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Another built-in pull request handler plugin can be used to check that
`towncrier <https://github.com/hawkowl/towncrier>`_ changelog changes in a pull
request are consistent with other details about the pull request (e.g. the pull
request number). To enable this plugin, include the following in your
``pyproject.toml`` file::

    [ tool.<your-bot-name>.towncrier_changelog ]
    enabled = true

This plugin has the following additional configuration items:

* ``verify_pr_number = true``: whether to check that the name of the towncrier
  file added is consistent with the pull request number.

* ``changelog_skip_label = "..."``: the name of a GitHub label which, if present,
  causes the towncrier changelog checks to be skipped.

* ``help_url = "..."``: this can be set to the URL to use for the status check
  'Details' link - you can set this to a URL explaining how to use towncrier
  for example.

By default, the comment/statuses posted by the bot should be informative, but
if you wish to change the wording of these messages, you can override them with
the following parameters:

* ``changelog_exists = "..."`` and ``changelog_missing = "..."``: the messages
  to use when a changelog entry exists or is missing.

* ``number_correct = "..."`` and ``number_incorrect = "..."``: the messages
  to use when a changelog entry has the correct or incorrect pull request number.

* ``type_correct = "..."`` and ``type_incorrect = "..."``: the messages
  to use when a changelog entry is not of the right type.

Custom plugin
^^^^^^^^^^^^^

If you want to write your own pull request checker, import
``pull_request_handler`` from baldrick as follows::

    from baldrick.plugins.github_pull_requests import pull_request_handler

then use it to decorate a function of the form::

    @pull_request_handler
    def check_changelog_consistency(pr_handler, repo_handler):
        ...

This function will be called with ``pr_handler``, an instance of
:class:`~baldrick.github.PullRequestHandler`, and ``repo_handler``,
an instance of :class:`~baldrick.github.RepoHandler` (click on
the class names to find out the available properties/methods).

Your function should then return either `None` (no check results), or
a dictionary where each key is the code name for one of the checks (this will
be used to match checks with previous checks, so make sure this is consistent
across calls), and the value should be a dictionary with two entries: ``state``,
which can be set to ``'failure'`` or ``'success'``, and ``description``, which
gives a description of the check results.
