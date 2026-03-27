@regression
Feature: Todo Application
  As a user of the Todo application
  I want to manage my todo items
  So that I can track tasks and stay organized

  Background:
    Given I open the Todo application

  @smoke @ui
  Scenario: Page loads with the correct title
    Then the page title should be "Todo App"
    And the add todo form should be visible
    And the filter bar should be visible

  @smoke @ui
  Scenario: Add a new todo item
    When I type "Buy groceries" in the todo input
    And I click the Add button
    Then I should see "Buy groceries" in the todo list
    And the input field should be empty

  @ui
  Scenario: Add multiple todo items
    When I add a todo "Task one"
    And I add a todo "Task two"
    And I add a todo "Task three"
    Then the todo list should contain 3 items

  @smoke @ui
  Scenario: Mark a todo as completed
    Given I have added a todo "Write tests"
    When I check the checkbox for "Write tests"
    Then "Write tests" should be shown as completed

  @ui
  Scenario: Unmark a completed todo
    Given I have added a todo "Review PR"
    And the todo "Review PR" is marked as completed
    When I uncheck the checkbox for "Review PR"
    Then "Review PR" should be shown as active

  @smoke @ui
  Scenario: Delete a todo item
    Given I have added a todo "Delete me"
    When I click the Delete button for "Delete me"
    Then "Delete me" should not be in the todo list

  @ui
  Scenario: Filter shows only active todos
    Given I have added a todo "Active task"
    And I have added a todo "Done task"
    And the todo "Done task" is marked as completed
    When I click the "Active" filter
    Then I should see "Active task" in the todo list
    And I should not see "Done task" in the todo list

  @ui
  Scenario: Filter shows only completed todos
    Given I have added a todo "Another active"
    And I have added a todo "Another done"
    And the todo "Another done" is marked as completed
    When I click the "Completed" filter
    Then I should see "Another done" in the todo list
    And I should not see "Another active" in the todo list

  @ui
  Scenario Outline: Filter buttons work correctly
    Given I have added a todo "<todo_title>"
    When I click the "<filter>" filter
    Then the "<filter>" filter button should be active

    Examples:
      | filter    | todo_title     |
      | All       | Filter test 1  |
      | Active    | Filter test 2  |
      | Completed | Filter test 3  |
