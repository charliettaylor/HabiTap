<script>
    import { Theme, OverflowMenu, OverflowMenuItem } from "carbon-components-svelte";
</script>

<header class="header">
  <div>
    <h1>HabiTap</h1>
   
    <OverflowMenu flipped size="xl">
      <OverflowMenuItem text="Login" primaryFocus />
      <OverflowMenuItem danger text="Sign up" />
      <OverflowMenuItem href="/docs" text="API documentation" />
      <span>
        <Theme
          render="toggle"
          toggle={{
            themes: ["g10", "g90"],
            labelA: "Dark mode",
            labelB: "Dark mode",
            hideLabel: true,
            size: "sm",
          }}
        />
      </span>
    </OverflowMenu>
  </div>
</header>

<style>
  header {
    margin: 1rem;
  }

  div {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
  }

  span {
    margin: 0.5rem;
  }
</style>