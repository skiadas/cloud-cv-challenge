# Github actions

- Can be triggered when an **event** occurs in your repository such as a pull request being opened or an issue being created.
- Your **workflow** contains one or more **jobs** which can run in **sequential** order or in **parallel**.
- Each job will run inside its own virtual machine runner, or inside a container
- Each job has one or more **steps** that either run a script that you define or run an **action**, which is a reusable extension that can simplify your workflow.
- Workflows are defined by a YAML file checked in to your repository and will run when triggered by an event in your repository, or they can be triggered manually, or at a defined schedule.
- `.github/workflows`
- For example:
  - build and test pull requests,
  - deploy your application every time a release is created,
  - add a label every time someone opens a new issue.
- You can [reference a workflow within another workflow](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows)


## Workflows

[Using workflows](https://docs.github.com/en/actions/using-workflows)

## Events

- A specific activity in a repository that triggers a workflow run.
  - can originate from GitHub when someone creates a pull request, opens an issue, or pushes a commit to a repository.
  - can also trigger a workflow run on a schedule, by posting to a REST API, or manually.
- [Events that trigger workflows](https://docs.github.com/en/actions/reference/events-that-trigger-workflows)

## Jobs

- Set of steps
- Run on the same runner
- Each step either a shell script or an action
- Executed in order
- Dependent on each other
- Can share data
- [Using Jobs](https://docs.github.com/en/actions/using-jobs)

## Actions

- A custom application for the GitHub Actions platform that performs a complex but frequently repeated task.
- Use an action to help reduce the amount of repetitive code that you write in your workflow files.
-  An action can pull your git repository from GitHub, set up the correct toolchain for your build environment, or set up the authentication to your cloud provider.
- You can write your own actions,
- or you can find actions to use in your workflows in the GitHub Marketplace.
- [Creating actions](https://docs.github.com/en/actions/creating-actions)
- [Community actions in Github Marketplace](https://github.com/marketplace/actions/)
- Sources:
  - The same repository as your workflow file, `actions` folder (`uses: ./.github/actions/...`)
  - Any public repository
  - A published Docker container image on Docker Hub


## Runners

- Servers that run your workflows
- Can [host your own runners](https://docs.github.com/en/actions/hosting-your-own-runners)

## Workflow YAML syntax

[Workflow syntax docs](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

- `name` how it shows up on github actions page
- `on` array of triggering events
- `jobs` the object of all the jobs to run
  - `runs-on` the OS for the runner
  - `steps` for the job
    - `uses` other actions
    - `run` scripts
